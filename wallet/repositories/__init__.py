"""Слой доступа к данным (паттерн Repository)."""

from wallet.repositories.account_repository import AccountRepository
from wallet.repositories.category_repository import CategoryRepository
from wallet.repositories.goal_repository import GoalRepository
from wallet.repositories.reminder_repository import ReminderRepository
from wallet.repositories.transaction_repository import TransactionRepository
from wallet.repositories.user_repository import UserRepository

__all__ = [
    "AccountRepository",
    "CategoryRepository",
    "GoalRepository",
    "ReminderRepository",
    "TransactionRepository",
    "UserRepository",
]
