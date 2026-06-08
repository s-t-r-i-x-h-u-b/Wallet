"""Общие фикстуры для тестов."""

from __future__ import annotations

from decimal import Decimal

import pytest

from wallet.app_context import AppContext
from wallet.core.db import Database
from wallet.models import Account


@pytest.fixture
def context() -> AppContext:
    """Контекст приложения с БД в памяти."""
    db = Database()  # in-memory
    db.connect()
    return AppContext(db)


@pytest.fixture
def account(context: AppContext) -> Account:
    """Тестовый счёт с нулевым балансом."""
    return context.accounts.add(
        Account(name="Наличные", type="cash", balance=Decimal("0"))
    )
