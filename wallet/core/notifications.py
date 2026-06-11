"""Локальные уведомления с реализациями под разные платформы.

Notifier — протокол отправки уведомления. Реализации:
- AndroidNotifier — системные уведомления Android напрямую через API (pyjnius)
  с созданием NotificationChannel (обязателен на Android 8+; без него система
  молча не показывает уведомление — типичная причина «не приходит»);
- PlyerNotifier — кроссплатформенная отправка через plyer (десктоп);
- NullNotifier — заглушка (тесты/среды без графической оболочки), запоминает
  отправленное.
"""

from __future__ import annotations

import os
from typing import Protocol, runtime_checkable


@runtime_checkable
class Notifier(Protocol):
    def notify(self, title: str, message: str) -> None: ...


class NullNotifier:
    """Заглушка: не показывает уведомления, но сохраняет их историю."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def notify(self, title: str, message: str) -> None:
        self.sent.append((title, message))


class PlyerNotifier:
    """Системные уведомления через plyer (десктоп-платформы)."""

    def notify(self, title: str, message: str) -> None:
        from plyer import notification

        notification.notify(title=title, message=message)


class AndroidNotifier:
    """Системные уведомления Android через нативный API (pyjnius).

    Создаёт канал уведомлений (Android 8+) и публикует уведомление напрямую
    через NotificationManager.
    """

    _channel_ready = False
    _counter = 1
    _CHANNEL_ID = "wallet_payments"

    def notify(self, title: str, message: str) -> None:
        from jnius import autoclass

        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        Builder = autoclass("android.app.Notification$Builder")
        NotificationManager = autoclass("android.app.NotificationManager")
        VERSION = autoclass("android.os.Build$VERSION")

        activity = PythonActivity.mActivity
        service = activity.getSystemService(Context.NOTIFICATION_SERVICE)

        if VERSION.SDK_INT >= 26:
            if not AndroidNotifier._channel_ready:
                NotificationChannel = autoclass("android.app.NotificationChannel")
                channel = NotificationChannel(
                    AndroidNotifier._CHANNEL_ID, "Платежи",
                    NotificationManager.IMPORTANCE_HIGH)
                service.createNotificationChannel(channel)
                AndroidNotifier._channel_ready = True
            builder = Builder(activity, AndroidNotifier._CHANNEL_ID)
        else:
            builder = Builder(activity)

        builder.setSmallIcon(activity.getApplicationInfo().icon)
        builder.setContentTitle(title)
        builder.setContentText(message)
        builder.setAutoCancel(True)

        AndroidNotifier._counter += 1
        service.notify(AndroidNotifier._counter, builder.build())


def default_notifier() -> Notifier:
    """Выбрать реализацию под текущую платформу."""
    # python-for-android выставляет переменную окружения ANDROID_ARGUMENT
    if os.environ.get("ANDROID_ARGUMENT") is not None:
        try:
            return AndroidNotifier()
        except Exception:  # noqa: BLE001  # nosec B110 - откат к plyer/Null ниже
            pass
    try:
        import plyer  # noqa: F401

        return PlyerNotifier()
    except Exception:  # noqa: BLE001
        return NullNotifier()
