"""Тесты сервиса напоминаний."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from wallet.models import Reminder


def test_upcoming_includes_due_and_excludes_future(context):
    today = date.today()
    context.reminder_service.schedule(
        Reminder(title="Аренда", amount=Decimal("15000"), due_date=today)
    )
    context.reminder_service.schedule(
        Reminder(title="Подписка", amount=Decimal("500"),
                 due_date=today + timedelta(days=30))
    )

    upcoming = context.reminder_service.upcoming(until=today)
    titles = [r.title for r in upcoming]
    assert "Аренда" in titles
    assert "Подписка" not in titles


def test_update_reminder(context):
    r = context.reminder_service.schedule(
        Reminder(title="Старое", amount=Decimal("100"), due_date=date.today())
    )
    context.reminder_service.update(r.id, title="Новое", amount=Decimal("250"))
    updated = context.reminders.get(r.id)
    assert updated.title == "Новое"
    assert updated.amount == Decimal("250")


def test_delete_reminder(context):
    r = context.reminder_service.schedule(
        Reminder(title="Удалить", amount=Decimal("100"), due_date=date.today())
    )
    context.reminder_service.delete(r.id)
    assert context.reminders.get(r.id) is None


def test_upcoming_with_horizon(context):
    today = date.today()
    context.reminder_service.schedule(
        Reminder(title="Кредит", amount=Decimal("8000"),
                 due_date=today + timedelta(days=5))
    )
    upcoming = context.reminder_service.upcoming(until=today + timedelta(days=7))
    assert [r.title for r in upcoming] == ["Кредит"]
