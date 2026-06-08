"""Тесты построения диаграмм."""

from __future__ import annotations

from decimal import Decimal

from wallet.models import Category, CategoryKind, Transaction, TransactionType

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _seed(context, account):
    food = context.categories.add(Category(name="Продукты", kind=CategoryKind.EXPENSE))
    context.transaction_service.add(
        Transaction(amount=Decimal("1000"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    context.transaction_service.add(
        Transaction(amount=Decimal("250"), type=TransactionType.EXPENSE,
                    account_id=account.id, category_id=food.id)
    )


def test_expenses_pie_creates_png(context, account, tmp_path):
    _seed(context, account)
    path = context.chart_service.expenses_pie(tmp_path / "pie.png")
    assert path.exists()
    assert path.read_bytes()[:8] == PNG_MAGIC


def test_income_expense_bar_creates_png(context, account, tmp_path):
    _seed(context, account)
    path = context.chart_service.income_expense_bar(tmp_path / "bar.png")
    assert path.exists()
    assert path.read_bytes()[:8] == PNG_MAGIC


def test_pie_with_no_data(context, tmp_path):
    path = context.chart_service.expenses_pie(tmp_path / "empty.png")
    assert path.exists()


def test_dynamics_chart_creates_png(context, account, tmp_path):
    _seed(context, account)
    path = context.chart_service.dynamics_chart(tmp_path / "dyn.png")
    assert path.exists()
    assert path.read_bytes()[:8] == PNG_MAGIC
