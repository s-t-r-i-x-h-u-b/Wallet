"""Базовый репозиторий и интерфейс доступа к данным."""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Интерфейс репозитория: единый контракт CRUD-операций."""

    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def get(self, entity_id: int) -> Optional[T]: ...

    @abstractmethod
    def list(self) -> list[T]: ...

    @abstractmethod
    def update(self, entity: T) -> None: ...

    @abstractmethod
    def delete(self, entity_id: int) -> None: ...


class BaseRepository(IRepository[T]):
    """Общая реализация для работы с одной таблицей SQLite."""

    table: str = ""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def _row_to_entity(self, row: sqlite3.Row) -> T:  # pragma: no cover
        raise NotImplementedError

    # Примечание по безопасности: имя таблицы (self.table) — внутренняя
    # константа класса-репозитория, не пользовательский ввод. Все значения,
    # приходящие извне, передаются параметрами запроса (?). Поэтому SQL-
    # инъекция невозможна, предупреждения B608 — ложные срабатывания.

    def get(self, entity_id: int) -> Optional[T]:
        cur = self.conn.execute(
            f"SELECT * FROM {self.table} WHERE id = ?", (entity_id,)  # nosec B608
        )
        row = cur.fetchone()
        return self._row_to_entity(row) if row else None

    def list(self) -> list[T]:
        cur = self.conn.execute(
            f"SELECT * FROM {self.table} ORDER BY id")  # nosec B608
        return [self._row_to_entity(r) for r in cur.fetchall()]

    def delete(self, entity_id: int) -> None:
        self.conn.execute(
            f"DELETE FROM {self.table} WHERE id = ?", (entity_id,))  # nosec B608
        self.conn.commit()
