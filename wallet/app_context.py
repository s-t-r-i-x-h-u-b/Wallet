"""Первичная интеграция компонентов приложения.

Класс AppContext связывает слой доступа к данным и слой бизнес-логики:
создаёт репозитории поверх общего соединения с БД и предоставляет готовые
сервисы слою представления.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from wallet.core.db import Database
from wallet.core.security import EncryptionManager, derive_key, generate_salt
from wallet.repositories import (
    AccountRepository,
    CategoryRepository,
    GoalRepository,
    ReminderRepository,
    TransactionRepository,
    UserRepository,
)
from wallet.services import (
    AnalyticsService,
    AuthService,
    CategoryService,
    GoalService,
    ReminderService,
    TransactionService,
)


class AppContext:
    """Контейнер зависимостей приложения."""

    def __init__(self, db: Database):
        self.db = db
        conn = db.connection

        # Слой доступа к данным
        self.users = UserRepository(conn)
        self.accounts = AccountRepository(conn)
        self.categories = CategoryRepository(conn)
        self.transactions = TransactionRepository(conn)
        self.goals = GoalRepository(conn)
        self.reminders = ReminderRepository(conn)

        # Слой бизнес-логики
        self.auth = AuthService(self.users)
        self.transaction_service = TransactionService(self.transactions, self.accounts)
        self.category_service = CategoryService(self.categories)
        self.goal_service = GoalService(self.goals)
        self.reminder_service = ReminderService(self.reminders)
        self.analytics = AnalyticsService(self.transactions, self.categories)

    @classmethod
    def open_encrypted(cls, path: str | Path, password: str, salt: Optional[bytes] = None) -> "AppContext":
        """Открыть зашифрованную БД, выведя ключ из пароля пользователя."""
        if salt is None:
            salt = generate_salt()
        encryption = EncryptionManager(derive_key(password, salt))
        db = Database(path=path, encryption=encryption)
        db.connect()
        return cls(db)

    def save(self) -> None:
        self.db.save()

    def close(self) -> None:
        self.db.close()
