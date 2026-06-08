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

    def monthly_dynamics(self, months: int = 6) -> list[tuple[str, Decimal, Decimal]]:
        """Динамика доходов и расходов по месяцам.

        Возвращает список кортежей (метка_месяца, доходы, расходы) за последние
        `months` месяцев, в которых были операции, в хронологическом порядке.
        """
        buckets: dict[tuple[int, int], dict[str, Decimal]] = {}
        for tx in self.transactions.list_filtered():
            key = (tx.created_at.year, tx.created_at.month)
            bucket = buckets.setdefault(
                key, {"income": Decimal("0"), "expense": Decimal("0")}
            )
            if tx.type == TransactionType.INCOME:
                bucket["income"] += tx.amount
            else:
                bucket["expense"] += tx.amount

        result: list[tuple[str, Decimal, Decimal]] = []
        for year, month in sorted(buckets)[-months:]:
            data = buckets[(year, month)]
            result.append((f"{month:02d}.{year}", data["income"], data["expense"]))
        return result
