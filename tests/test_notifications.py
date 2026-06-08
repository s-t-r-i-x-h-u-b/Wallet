"""Тесты уведомлений и рассылки по напоминаниям."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from wallet.core.notifications import Notifier, NullNotifier, default_notifier
from wallet.models import Reminder


def test_null_notifier_records_messages():
    notifier = NullNotifier()
    notifier.notify("Заголовок", "Текст")
    assert notifier.sent == [("Заголовок", "Текст")]


def test_default_notifier_is_notifier():
    assert isinstance(default_notifier(), Notifier)


def test_notify_due_sends_only_due(context):
    today = date.today()
    context.reminder_service.schedule(
        Reminder(title="Аренда", amount=Decimal("15000"), due_date=today)
    )
    context.reminder_service.schedule(
        Reminder(title="Будущее", amount=Decimal("100"),
                 due_date=today + timedelta(days=10))
    )
    notifier = NullNotifier()
    count = context.reminder_service.notify_due(notifier, until=today)
    assert count == 1
    assert "Аренда" in notifier.sent[0][0]
