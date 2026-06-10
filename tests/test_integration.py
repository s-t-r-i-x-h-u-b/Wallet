"""Интеграционные тесты: сквозной сценарий и персистентность хранилища.

Проверяется совместная работа всех слоёв (vault → БД → репозитории →
сервисы) и сохранение данных в зашифрованном хранилище между сессиями.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest

from wallet.app_context import AppContext
from wallet.core import vault
from wallet.models import Reminder, Transaction, TransactionType


def test_full_scenario_and_persistence(tmp_path):
    # --- сессия 1: создание хранилища и ввод данных ---
    ctx = AppContext.init_vault(tmp_path, "secret")
    ctx.category_service.ensure_defaults()
    salary = next(c for c in ctx.category_service.list() if c.name == "Зарплата")
    food = next(c for c in ctx.category_service.list() if c.name == "Продукты")

    account = ctx.account_service.create("Карта", initial_balance=Decimal("0"))

    ctx.transaction_service.add(Transaction(
        amount=Decimal("50000"), type=TransactionType.INCOME,
        account_id=account.id, category_id=salary.id, note="Зарплата",
        created_at=datetime(2026, 5, 5)))
    ctx.transaction_service.add(Transaction(
        amount=Decimal("1500"), type=TransactionType.EXPENSE,
        account_id=account.id, category_id=food.id, note="Магазин",
        created_at=datetime(2026, 5, 7)))

    goal = ctx.goal_service.create("Отпуск", Decimal("100000"))
    ctx.goal_service.contribute(goal.id, Decimal("20000"))
    ctx.reminder_service.schedule(Reminder(
        title="Аренда", amount=Decimal("25000"), due_date=date(2026, 6, 1),
        is_repeating=True, period="monthly"))

    # баланс и аналитика в текущей сессии
    assert ctx.account_service.total_balance() == Decimal("48500")
    totals = ctx.analytics.income_vs_expense()
    assert totals["income"] == Decimal("50000")
    assert totals["expense"] == Decimal("1500")
    assert ctx.analytics.expenses_by_category()["Продукты"] == Decimal("1500")

    ctx.save()
    ctx.close()

    # --- сессия 2: повторное открытие тем же паролем ---
    reopened = AppContext.open_vault(tmp_path, "secret")
    assert reopened.account_service.total_balance() == Decimal("48500")
    assert len(reopened.transaction_service.list()) == 2
    assert reopened.goal_service.list()[0].current_amount == Decimal("20000")
    assert reopened.reminder_service.list()[0].title == "Аренда"
    reopened.close()


def test_persistence_rejects_wrong_password(tmp_path):
    ctx = AppContext.init_vault(tmp_path, "right")
    ctx.account_service.create("Наличные", initial_balance=Decimal("100"))
    ctx.save()
    ctx.close()

    with pytest.raises(vault.InvalidPasswordError):
        AppContext.open_vault(tmp_path, "wrong")


def test_password_change_end_to_end(tmp_path):
    ctx = AppContext.init_vault(tmp_path, "old")
    ctx.account_service.create("Карта", initial_balance=Decimal("500"))
    ctx.change_password("new")
    ctx.close()

    with pytest.raises(vault.InvalidPasswordError):
        AppContext.open_vault(tmp_path, "old")
    reopened = AppContext.open_vault(tmp_path, "new")
    assert reopened.account_service.total_balance() == Decimal("500")
    reopened.close()
