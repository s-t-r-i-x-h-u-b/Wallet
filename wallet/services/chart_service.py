"""Построение диаграмм для визуализации финансовых данных.

Используется неинтерактивный backend matplotlib (Agg), что позволяет
сохранять диаграммы в файлы изображений без графической оболочки. В UI
полученные PNG отображаются как картинки.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # backend без графической оболочки
import matplotlib.pyplot as plt  # noqa: E402

from wallet.services.analytics_service import AnalyticsService  # noqa: E402


class ChartService:
    """Готовит изображения диаграмм на основе данных AnalyticsService."""

    def __init__(self, analytics: AnalyticsService):
        self.analytics = analytics

    def expenses_pie(
        self,
        path: str | Path,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Path:
        """Круговая диаграмма структуры расходов по категориям."""
        data = self.analytics.expenses_by_category(date_from, date_to)
        fig, ax = plt.subplots()
        if data:
            ax.pie(
                [float(v) for v in data.values()],
                labels=list(data.keys()),
                autopct="%1.1f%%",
            )
        else:
            ax.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        ax.set_title("Структура расходов по категориям")
        fig.savefig(path)
        plt.close(fig)
        return Path(path)

    def income_expense_bar(
        self,
        path: str | Path,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Path:
        """Столбчатая диаграмма соотношения доходов и расходов."""
        totals = self.analytics.income_vs_expense(date_from, date_to)
        fig, ax = plt.subplots()
        ax.bar(
            ["Доходы", "Расходы"],
            [float(totals["income"]), float(totals["expense"])],
            color=["#4caf50", "#e53935"],
        )
        ax.set_ylabel("Сумма")
        ax.set_title("Доходы и расходы")
        fig.savefig(path)
        plt.close(fig)
        return Path(path)
