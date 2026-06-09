"""Построение диаграмм для визуализации финансовых данных.

Используется неинтерактивный backend matplotlib (Agg), что позволяет
сохранять диаграммы в файлы изображений без графической оболочки. В UI
полученные PNG отображаются как картинки.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from wallet.services.analytics_service import AnalyticsService


class ChartService:
    """Готовит изображения диаграмм на основе данных AnalyticsService.

    matplotlib импортируется по требованию: библиотека тяжёлая и не всегда
    доступна на мобильной платформе, поэтому её отсутствие не должно мешать
    запуску приложения. Если matplotlib не установлен, методы построения
    диаграмм возбуждают ImportError, который обрабатывается слоем интерфейса.
    """

    def __init__(self, analytics: AnalyticsService):
        self.analytics = analytics

    @staticmethod
    def _pyplot():
        import matplotlib

        matplotlib.use("Agg")  # backend без графической оболочки
        import matplotlib.pyplot as plt

        return plt

    def expenses_pie(
        self,
        path: str | Path,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Path:
        """Круговая диаграмма структуры расходов по категориям."""
        plt = self._pyplot()
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
        plt = self._pyplot()
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

    def dynamics_chart(
        self,
        path: str | Path,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Path:
        """Диаграмма динамики доходов и расходов по месяцам за период."""
        plt = self._pyplot()
        data = self.analytics.monthly_dynamics(date_from, date_to)
        labels = [d[0] for d in data]
        incomes = [float(d[1]) for d in data]
        expenses = [float(d[2]) for d in data]

        fig, ax = plt.subplots()
        if data:
            positions = range(len(labels))
            width = 0.4
            ax.bar([p - width / 2 for p in positions], incomes, width,
                   label="Доходы", color="#4caf50")
            ax.bar([p + width / 2 for p in positions], expenses, width,
                   label="Расходы", color="#e53935")
            ax.set_xticks(list(positions))
            ax.set_xticklabels(labels, rotation=45, ha="right")
            ax.legend()
        else:
            ax.text(0.5, 0.5, "Нет данных", ha="center", va="center")
        ax.set_title("Динамика по месяцам")
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        return Path(path)
