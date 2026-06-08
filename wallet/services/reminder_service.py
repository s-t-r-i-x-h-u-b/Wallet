"""Сервис напоминаний о платежах."""

from __future__ import annotations

from datetime import date

from wallet.models import Reminder
from wallet.repositories import ReminderRepository


class ReminderService:
    """Создание напоминаний и выборка предстоящих платежей.

    Фактическая доставка уведомлений выполняется кроссплатформенно через
    библиотеку plyer на уровне слоя представления; сервис отвечает за
    хранение и выборку напоминаний.
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
