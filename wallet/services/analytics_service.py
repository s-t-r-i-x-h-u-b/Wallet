"""Сервис аналитики и подготовки данных для визуализации."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from wallet.models import TransactionType
from wallet.repositories import CategoryRepository, TransactionRepository


class AnalyticsService:
    """Агрегация финансовых данных для диаграмм и сводок."""

    def __init__(
        self,
        transactions: TransactionRepository,
        categories: CategoryRepository,
    ):
        self.transactions = transactions
        self.categories = categories

    def expenses_by_category(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict[str, Decimal]:
        """Суммы расходов, сгруппированные по названию категории."""
        cat_names = {c.id: c.name for c in self.categories.list()}
        result: dict[str, Decimal] = {}
        txs = self.transactions.list_filtered(
            tx_type=TransactionType.EXPENSE, date_from=date_from, date_to=date_to
        )
        for tx in txs:
            name = cat_names.get(tx.category_id, "Без категории")
            result[name] = result.get(name, Decimal("0")) + tx.amount
        return result

    def income_vs_expense(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> dict[str, Decimal]:
        """Итоговые суммы доходов и расходов за период."""
        income = sum(
            (t.amount for t in self.transactions.list_filtered(
                tx_type=TransactionType.INCOME, date_from=date_from, date_to=date_to)),
            Decimal("0"),
        )
        expense = sum(
            (t.amount for t in self.transactions.list_filtered(
                tx_type=TransactionType.EXPENSE, date_from=date_from, date_to=date_to)),
            Decimal("0"),
        )
        return {"income": income, "expense": expense, "balance": income - expense}
