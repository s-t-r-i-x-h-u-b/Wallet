"""Репозиторий транзакций."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import Optional

from wallet.models import Transaction, TransactionType
from wallet.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    table = "transactions"

    def _row_to_entity(self, row: sqlite3.Row) -> Transaction:
        return Transaction(
            id=row["id"],
            account_id=row["account_id"],
            category_id=row["category_id"],
            amount=Decimal(row["amount"]),
            type=TransactionType(row["type"]),
            note=row["note"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def add(self, entity: Transaction) -> Transaction:
        cur = self.conn.execute(
            "INSERT INTO transactions "
            "(account_id, category_id, amount, type, note, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                entity.account_id,
                entity.category_id,
                str(entity.amount),
                entity.type.value,
                entity.note,
                entity.created_at.isoformat(),
            ),
        )
        self.conn.commit()
        entity.id = cur.lastrowid
        return entity

    def update(self, entity: Transaction) -> None:
        self.conn.execute(
            "UPDATE transactions SET account_id = ?, category_id = ?, amount = ?, "
            "type = ?, note = ? WHERE id = ?",
            (
                entity.account_id,
                entity.category_id,
                str(entity.amount),
                entity.type.value,
                entity.note,
                entity.id,
            ),
        )
        self.conn.commit()

    def list_filtered(
        self,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tx_type: Optional[TransactionType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[Transaction]:
        """Вернуть транзакции с фильтрацией по счёту, категории, типу, периоду."""
        clauses: list[str] = []
        params: list = []
        if account_id is not None:
            clauses.append("account_id = ?")
            params.append(account_id)
        if category_id is not None:
            clauses.append("category_id = ?")
            params.append(category_id)
        if tx_type is not None:
            clauses.append("type = ?")
            params.append(tx_type.value)
        if date_from is not None:
            clauses.append("created_at >= ?")
            params.append(date_from.isoformat())
        if date_to is not None:
            clauses.append("created_at <= ?")
            params.append(date_to.isoformat())

        # where собирается только из внутренних имён столбцов; пользовательские
        # значения передаются параметрами (params) -> инъекция невозможна.
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        cur = self.conn.execute(
            f"SELECT * FROM transactions{where} ORDER BY created_at DESC",  # nosec B608
            params,
        )
        return [self._row_to_entity(r) for r in cur.fetchall()]
