"""Первичная интеграция компонентов приложения.

Класс AppContext связывает слой доступа к данным и слой бизнес-логики:
создаёт репозитории поверх общего соединения с БД и предоставляет готовые
сервисы слою представления.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from wallet.core.db import Database
from wallet.core.notifications import Notifier, default_notifier
from wallet.repositories import (
    AccountRepository,
    CategoryRepository,
    GoalRepository,
    ReminderRepository,
    TransactionRepository,
    UserRepository,
)
from wallet.services import (
    AccountService,
    AnalyticsService,
    AuthService,
    CategoryService,
    ChartService,
    GoalService,
    ReminderService,
    TransactionService,
)


class AppContext:
    """Контейнер зависимостей приложения."""

    def __init__(self, db: Database, notifier: Optional[Notifier] = None):
        self.db = db
        self.notifier = notifier or default_notifier()
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
        self.account_service = AccountService(self.accounts)
        self.transaction_service = TransactionService(self.transactions, self.accounts)
        self.category_service = CategoryService(self.categories)
        self.goal_service = GoalService(self.goals)
        self.reminder_service = ReminderService(self.reminders)
        self.analytics = AnalyticsService(self.transactions, self.categories)
        self.chart_service = ChartService(self.analytics)

    @classmethod
    def init_vault(cls, data_dir: str | Path, password: str) -> "AppContext":
        """Создать новое зашифрованное хранилище и открыть контекст."""
        from wallet.core import vault

        return cls(vault.init_vault(data_dir, password))

    @classmethod
    def open_vault(cls, data_dir: str | Path, password: str) -> "AppContext":
        """Открыть существующее хранилище по паролю."""
        from wallet.core import vault

        return cls(vault.open_vault(data_dir, password))

    def change_password(self, new_password: str) -> None:
        """Сменить пароль (пин-код) хранилища."""
        from wallet.core import vault

        vault.change_password(self.db, new_password)

    def save(self) -> None:
        self.db.save()

    def close(self) -> None:
        self.db.close()
