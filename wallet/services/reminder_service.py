"""Сервис напоминаний о платежах."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from decimal import Decimal

from wallet.core.notifications import Notifier
from wallet.models import Reminder
from wallet.repositories import ReminderRepository


def _add_months(d: date, months: int) -> date:
    """Прибавить месяцы с корректировкой числа под длину месяца."""
    index = d.month - 1 + months
    year = d.year + index // 12
    month = index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def next_due_date(current: date, period: str) -> date:
    """Вычислить следующую дату платежа по периодичности."""
    if period == "daily":
        return current + timedelta(days=1)
    if period == "weekly":
        return current + timedelta(weeks=1)
    if period == "monthly":
        return _add_months(current, 1)
    if period == "yearly":
        return _add_months(current, 12)
    raise ValueError(f"Неизвестная периодичность: {period!r}")


class ReminderService:
    """Создание напоминаний, выборка предстоящих и рассылка уведомлений.

    Доставка уведомлений делегируется объекту Notifier (plyer на устройстве,
    заглушка в средах без графической оболочки).
    """

    def __init__(self, reminders: ReminderRepository):
        self.reminders = reminders

    def schedule(self, reminder: Reminder) -> Reminder:
        if reminder.amount <= 0:
            raise ValueError("Сумма напоминания должна быть положительной")
        return self.reminders.add(reminder)

    def upcoming(self, until: date | None = None) -> list[Reminder]:
        """Напоминания со сроком не позднее указанной даты (по умолчанию сегодня)."""
        return self.reminders.list_upcoming(until or date.today())

    def list(self) -> list[Reminder]:
        return self.reminders.list()

    def advance(self, reminder_id: int) -> Reminder:
        """Перенести повторяющееся напоминание на следующий период."""
        reminder = self.reminders.get(reminder_id)
        if reminder is None:
            raise ValueError("Напоминание не найдено")
        if reminder.is_repeating and reminder.period:
            reminder.due_date = next_due_date(reminder.due_date, reminder.period)
            self.reminders.update(reminder)
        return reminder

    def update(
        self,
        reminder_id: int,
        title: str | None = None,
        amount: Decimal | None = None,
        due_date: date | None = None,
    ) -> Reminder:
        """Изменить название, сумму и/или срок платежа."""
        reminder = self.reminders.get(reminder_id)
        if reminder is None:
            raise ValueError("Напоминание не найдено")
        if title is not None:
            if not title.strip():
                raise ValueError("Название не может быть пустым")
            reminder.title = title.strip()
        if amount is not None:
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            reminder.amount = amount
        if due_date is not None:
            reminder.due_date = due_date
        self.reminders.update(reminder)
        return reminder

    def delete(self, reminder_id: int) -> None:
        self.reminders.delete(reminder_id)

    def notify_due(self, notifier: Notifier, until: date | None = None) -> int:
        """Разослать уведомления по наступившим напоминаниям. Возвращает их число."""
        due = self.upcoming(until)
        for reminder in due:
            notifier.notify(
                title=f"Платёж: {reminder.title}",
                message=f"Сумма {reminder.amount}, срок {reminder.due_date}",
            )
        return len(due)
