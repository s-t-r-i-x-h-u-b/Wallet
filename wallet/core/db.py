"""Доступ к базе данных SQLite с шифрованием файла «в покое».

Во время работы база данных находится в оперативной памяти (:memory:).
При сохранении содержимое сериализуется и шифруется (AES-256-GCM), при
открытии — расшифровывается и загружается обратно. Без корректного ключа
(выведенного из пароля пользователя) данные недоступны.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from wallet.core.security import EncryptionManager

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER REFERENCES users(id),
    name     TEXT NOT NULL,
    type     TEXT NOT NULL,
    balance  TEXT NOT NULL,
    currency TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER REFERENCES users(id),
    name          TEXT NOT NULL,
    kind          TEXT NOT NULL,
    icon          TEXT,
    is_predefined INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id  INTEGER NOT NULL REFERENCES accounts(id),
    category_id INTEGER REFERENCES categories(id),
    amount      TEXT NOT NULL,
    type        TEXT NOT NULL,
    note        TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS goals (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER REFERENCES users(id),
    title          TEXT NOT NULL,
    target_amount  TEXT NOT NULL,
    current_amount TEXT NOT NULL DEFAULT '0',
    deadline       TEXT
);

CREATE TABLE IF NOT EXISTS reminders (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id  INTEGER REFERENCES categories(id),
    title        TEXT NOT NULL,
    amount       TEXT NOT NULL,
    due_date     TEXT NOT NULL,
    is_repeating INTEGER NOT NULL DEFAULT 0,
    period       TEXT
);
"""


class Database:
    """Обёртка над соединением SQLite с поддержкой шифрования файла.

    :param path: путь к зашифрованному файлу БД (.db.enc). Если None —
        база существует только в памяти (удобно для тестов).
    :param encryption: менеджер шифрования; обязателен для работы с файлом.
    """

    def __init__(
        self,
        path: Optional[str | Path] = None,
        encryption: Optional[EncryptionManager] = None,
    ):
        self.path = Path(path) if path else None
        self.encryption = encryption
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("База данных не открыта. Вызовите connect().")
        return self._conn

    def connect(self) -> sqlite3.Connection:
        """Открыть БД: расшифровать существующий файл или создать новую."""
        self._conn = sqlite3.connect(":memory:")
        self._conn.row_factory = sqlite3.Row

        if self.path and self.path.exists():
            if self.encryption is None:
                raise ValueError("Для открытия зашифрованного файла нужен ключ")
            plaintext = self.encryption.decrypt(self.path.read_bytes())
            self._conn.deserialize(plaintext)

        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)
        self._conn.commit()
        return self._conn

    def save(self) -> None:
        """Сериализовать БД, зашифровать и записать в файл."""
        if not self.path:
            return  # in-memory режим — сохранять некуда
        if self.encryption is None:
            raise ValueError("Для сохранения зашифрованного файла нужен ключ")
        data = self.connection.serialize()
        self.path.write_bytes(self.encryption.encrypt(data))

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None:
            self.save()
        self.close()
