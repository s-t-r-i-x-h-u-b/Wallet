"""Локальные уведомления (кроссплатформенно через plyer) с запасным вариантом.

Notifier — это протокол отправки уведомлений. PlyerNotifier использует
системные уведомления через plyer; NullNotifier ничего не показывает, но
запоминает отправленное (удобно для тестов и сред без графической оболочки).
"""

from __future__ import annotations

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
    """Системные уведомления через plyer."""

    def notify(self, title: str, message: str) -> None:
        from plyer import notification  # импорт по месту — backend зависит от ОС

        notification.notify(title=title, message=message)


def default_notifier() -> Notifier:
    """Вернуть PlyerNotifier, если plyer доступен, иначе NullNotifier."""
    try:
        import plyer  # noqa: F401

        return PlyerNotifier()
    except Exception:  # noqa: BLE001
        return NullNotifier()
