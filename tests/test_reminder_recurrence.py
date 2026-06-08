"""Тесты периодичности напоминаний."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from wallet.models import Reminder
from wallet.services.reminder_service import next_due_date


@pytest.mark.parametrize(
    "current,period,expected",
    [
        (date(2026, 1, 15), "daily", date(2026, 1, 16)),
        (date(2026, 1, 15), "weekly", date(2026, 1, 22)),
        (date(2026, 1, 31), "monthly", date(2026, 2, 28)),  # корректировка под февраль
        (date(2026, 1, 15), "yearly", date(2027, 1, 15)),
    ],
)
def test_next_due_date(current, period, expected):
    assert next_due_date(current, period) == expected


def test_unknown_period_rejected():
    with pytest.raises(ValueError):
        next_due_date(date.today(), "hourly")


def test_advance_repeating_reminder(context):
    r = context.reminder_service.schedule(
        Reminder(title="Аренда", amount=Decimal("15000"),
                 due_date=date(2026, 1, 31), is_repeating=True, period="monthly")
    )
    advanced = context.reminder_service.advance(r.id)
    assert advanced.due_date == date(2026, 2, 28)


def test_advance_non_repeating_keeps_date(context):
    r = context.reminder_service.schedule(
        Reminder(title="Разовый", amount=Decimal("500"), due_date=date(2026, 1, 10))
    )
    advanced = context.reminder_service.advance(r.id)
    assert advanced.due_date == date(2026, 1, 10)
