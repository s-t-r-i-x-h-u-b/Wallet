"""Репозиторий напоминаний о платежах."""

from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal

from wallet.models import Reminder
from wallet.repositories.base import BaseRepository


class ReminderRepository(BaseRepository[Reminder]):
    table = "reminders"

    def _row_to_entity(self, row: sqlite3.Row) -> Reminder:
        return Reminder(
            id=row["id"],
            category_id=row["category_id"],
            title=row["title"],
            amount=Decimal(row["amount"]),
            due_date=date.fromisoformat(row["due_date"]),
            is_repeating=bool(row["is_repeating"]),
            period=row["period"] or "",
        )

    def add(self, entity: Reminder) -> Reminder:
        cur = self.conn.execute(
            "INSERT INTO reminders "
            "(category_id, title, amount, due_date, is_repeating, period) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                entity.category_id,
                entity.title,
                str(entity.amount),
                entity.due_date.isoformat(),
                int(entity.is_repeating),
                entity.period,
            ),
        )
        self.conn.commit()
        entity.id = cur.lastrowid
        return entity

    def update(self, entity: Reminder) -> None:
        self.conn.execute(
            "UPDATE reminders SET title = ?, amount = ?, due_date = ?, "
            "is_repeating = ?, period = ? WHERE id = ?",
            (
                entity.title,
                str(entity.amount),
                entity.due_date.isoformat(),
                int(entity.is_repeating),
                entity.period,
                entity.id,
            ),
        )
        self.conn.commit()

    def list_upcoming(self, until: date) -> list[Reminder]:
        """Напоминания со сроком не позднее указанной даты."""
        cur = self.conn.execute(
            "SELECT * FROM reminders WHERE due_date <= ? ORDER BY due_date",
            (until.isoformat(),),
        )
        return [self._row_to_entity(r) for r in cur.fetchall()]
