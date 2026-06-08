"""Тесты сервиса аналитики."""

from __future__ import annotations

from decimal import Decimal

from wallet.models import Category, CategoryKind, Transaction, TransactionType


def _add_expense(context, account, category_id, amount):
    context.transaction_service.add(
        Transaction(amount=Decimal(amount), type=TransactionType.EXPENSE,
                    account_id=account.id, category_id=category_id)
    )


def test_expenses_by_category(context, account):
    food = context.categories.add(Category(name="Продукты", kind=CategoryKind.EXPENSE))
    transport = context.categories.add(Category(name="Транспорт", kind=CategoryKind.EXPENSE))

    _add_expense(context, account, food.id, "300")
    _add_expense(context, account, food.id, "200")
    _add_expense(context, account, transport.id, "150")

    by_cat = context.analytics.expenses_by_category()
    assert by_cat["Продукты"] == Decimal("500")
    assert by_cat["Транспорт"] == Decimal("150")


def test_monthly_dynamics(context, account):
    from datetime import datetime

    context.transaction_service.add(
        Transaction(amount=Decimal("1000"), type=TransactionType.INCOME,
                    account_id=account.id, created_at=datetime(2026, 1, 10))
    )
    context.transaction_service.add(
        Transaction(amount=Decimal("300"), type=TransactionType.EXPENSE,
                    account_id=account.id, created_at=datetime(2026, 1, 20))
    )
    context.transaction_service.add(
        Transaction(amount=Decimal("500"), type=TransactionType.INCOME,
                    account_id=account.id, created_at=datetime(2026, 2, 5))
    )
    dynamics = context.analytics.monthly_dynamics()
    assert dynamics == [
        ("01.2026", Decimal("1000"), Decimal("300")),
        ("02.2026", Decimal("500"), Decimal("0")),
    ]


def test_income_vs_expense(context, account):
    context.transaction_service.add(
        Transaction(amount=Decimal("2000"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    context.transaction_service.add(
        Transaction(amount=Decimal("750"), type=TransactionType.EXPENSE,
                    account_id=account.id)
    )
    totals = context.analytics.income_vs_expense()
    assert totals["income"] == Decimal("2000")
    assert totals["expense"] == Decimal("750")
    assert totals["balance"] == Decimal("1250")
