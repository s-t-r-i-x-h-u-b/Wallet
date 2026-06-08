"""Репозиторий финансовых целей."""

from __future__ import annotations

import sqlite3
from datetime import date
from decimal import Decimal

from wallet.models import Goal
from wallet.repositories.base import BaseRepository


class GoalRepository(BaseRepository[Goal]):
    table = "goals"

    def _row_to_entity(self, row: sqlite3.Row) -> Goal:
        return Goal(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            target_amount=Decimal(row["target_amount"]),
            current_amount=Decimal(row["current_amount"]),
            deadline=date.fromisoformat(row["deadline"]) if row["deadline"] else None,
        )

    def add(self, entity: Goal) -> Goal:
        cur = self.conn.execute(
            "INSERT INTO goals "
            "(user_id, title, target_amount, current_amount, deadline) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                entity.user_id,
                entity.title,
                str(entity.target_amount),
                str(entity.current_amount),
                entity.deadline.isoformat() if entity.deadline else None,
            ),
        )
        self.conn.commit()
        entity.id = cur.lastrowid
        return entity

    def update(self, entity: Goal) -> None:
        self.conn.execute(
            "UPDATE goals SET title = ?, target_amount = ?, current_amount = ?, "
            "deadline = ? WHERE id = ?",
            (
                entity.title,
                str(entity.target_amount),
                str(entity.current_amount),
                entity.deadline.isoformat() if entity.deadline else None,
                entity.id,
            ),
        )
        self.conn.commit()
