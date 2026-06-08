"""Модели (сущности) предметной области «персональные финансы».

Денежные суммы хранятся в виде Decimal во избежание ошибок округления,
характерных для чисел с плавающей точкой.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional


class TransactionType(str, Enum):
    """Тип транзакции."""

    INCOME = "income"
    EXPENSE = "expense"


class CategoryKind(str, Enum):
    """Принадлежность категории к доходам или расходам."""

    INCOME = "income"
    EXPENSE = "expense"


@dataclass
class User:
    """Пользователь приложения."""

    name: str
    password_hash: str
    salt: str
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Account:
    """Счёт пользователя (наличные, карта, электронный кошелёк)."""

    name: str
    type: str = "cash"
    balance: Decimal = Decimal("0")
    currency: str = "RUB"
    user_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class Category:
    """Категория операции."""

    name: str
    kind: CategoryKind = CategoryKind.EXPENSE
    icon: str = ""
    is_predefined: bool = False
    user_id: Optional[int] = None
    id: Optional[int] = None


@dataclass
class Transaction:
    """Финансовая операция (доход или расход)."""

    amount: Decimal
    type: TransactionType
    account_id: int
    category_id: Optional[int] = None
    note: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None


@dataclass
class Goal:
    """Финансовая цель пользователя."""

    title: str
    target_amount: Decimal
    current_amount: Decimal = Decimal("0")
    deadline: Optional[date] = None
    user_id: Optional[int] = None
    id: Optional[int] = None

    @property
    def progress(self) -> float:
        """Доля достижения цели в диапазоне [0.0, 1.0]."""
        if self.target_amount <= 0:
            return 0.0
        return min(float(self.current_amount / self.target_amount), 1.0)

    @property
    def is_reached(self) -> bool:
        return self.current_amount >= self.target_amount


@dataclass
class Reminder:
    """Напоминание о предстоящем платеже."""

    title: str
    amount: Decimal
    due_date: date
    category_id: Optional[int] = None
    is_repeating: bool = False
    period: str = ""
    id: Optional[int] = None
