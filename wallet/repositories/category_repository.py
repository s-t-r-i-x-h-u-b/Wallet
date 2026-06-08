"""Репозиторий категорий."""

from __future__ import annotations

import sqlite3

from wallet.models import Category, CategoryKind
from wallet.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    table = "categories"

    def _row_to_entity(self, row: sqlite3.Row) -> Category:
        return Category(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            kind=CategoryKind(row["kind"]),
            icon=row["icon"] or "",
            is_predefined=bool(row["is_predefined"]),
        )

    def add(self, entity: Category) -> Category:
        cur = self.conn.execute(
            "INSERT INTO categories (user_id, name, kind, icon, is_predefined) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                entity.user_id,
                entity.name,
                entity.kind.value,
                entity.icon,
                int(entity.is_predefined),
            ),
        )
        self.conn.commit()
        entity.id = cur.lastrowid
        return entity

    def update(self, entity: Category) -> None:
        self.conn.execute(
            "UPDATE categories SET name = ?, kind = ?, icon = ? WHERE id = ?",
            (entity.name, entity.kind.value, entity.icon, entity.id),
        )
        self.conn.commit()
