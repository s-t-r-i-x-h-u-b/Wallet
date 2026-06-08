"""Репозиторий пользователей."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

from wallet.models import User
from wallet.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    table = "users"

    def _row_to_entity(self, row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            name=row["name"],
            password_hash=row["password_hash"],
            salt=row["salt"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def add(self, entity: User) -> User:
        cur = self.conn.execute(
            "INSERT INTO users (name, password_hash, salt, created_at) "
            "VALUES (?, ?, ?, ?)",
            (
                entity.name,
                entity.password_hash,
                entity.salt,
                entity.created_at.isoformat(),
            ),
        )
        self.conn.commit()
        entity.id = cur.lastrowid
        return entity

    def update(self, entity: User) -> None:
        self.conn.execute(
            "UPDATE users SET name = ?, password_hash = ?, salt = ? WHERE id = ?",
            (entity.name, entity.password_hash, entity.salt, entity.id),
        )
        self.conn.commit()

    def get_by_name(self, name: str) -> Optional[User]:
        cur = self.conn.execute("SELECT * FROM users WHERE name = ?", (name,))
        row = cur.fetchone()
        return self._row_to_entity(row) if row else None
