"""Репозиторий счетов."""

from __future__ import annotations

import sqlite3
from decimal import Decimal

from wallet.models import Account
from wallet.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    table = "accounts"

    def _row_to_entity(self, row: sqlite3.Row) -> Account:
        return Account(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            type=row["type"],
            balance=Decimal(row["balance"]),
            currency=row["currency"],
        )

    def add(self, entity: Account) -> Account:
        cur = self.conn.execute(
            "INSERT INTO accounts (user_id, name, type, balance, currency) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                entity.user_id,
                entity.name,
                entity.type,
                str(entity.balance),
                entity.currency,
            ),
        )
        self.conn.commit()
        entity.id = cur.lastrowid
        return entity

    def update(self, entity: Account) -> None:
        self.conn.execute(
            "UPDATE accounts SET name = ?, type = ?, balance = ?, currency = ? "
            "WHERE id = ?",
            (entity.name, entity.type, str(entity.balance), entity.currency, entity.id),
        )
        self.conn.commit()
