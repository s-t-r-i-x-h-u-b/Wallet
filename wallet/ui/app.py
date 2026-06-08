"""Прототип пользовательского интерфейса на Kivy.

Kivy импортируется «мягко»: если фреймворк не установлен (например, в среде
запуска тестов), модуль остаётся импортируемым, а попытка запустить GUI
сообщает о необходимости установить зависимости. Это обеспечивает
тестируемость бизнес-логики независимо от наличия графической среды.
"""

from __future__ import annotations

from decimal import Decimal

try:  # pragma: no cover - наличие Kivy зависит от среды
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label

    KIVY_AVAILABLE = True
except Exception:  # noqa: BLE001
    KIVY_AVAILABLE = False
    App = object  # type: ignore

from wallet.app_context import AppContext


if KIVY_AVAILABLE:

    class DashboardLayout(BoxLayout):
        """Главный экран: сводка по балансу и последним операциям."""

        def __init__(self, context: AppContext, **kwargs):
            super().__init__(orientation="vertical", **kwargs)
            self.context = context
            self._build()

        def _build(self) -> None:
            totals = self.context.analytics.income_vs_expense()
            self.add_widget(Label(text="Wallet — учёт личных финансов",
                                  font_size="20sp", size_hint_y=0.2))
            self.add_widget(Label(
                text=(f"Доходы: {totals['income']}   "
                      f"Расходы: {totals['expense']}   "
                      f"Баланс: {totals['balance']}"),
                size_hint_y=0.2,
            ))
            recent = self.context.transaction_service.list()[:5]
            for tx in recent:
                self.add_widget(Label(text=f"{tx.type.value}: {tx.amount} — {tx.note}"))

    class WalletApp(App):
        """Корневое приложение Kivy."""

        def __init__(self, context: AppContext, **kwargs):
            super().__init__(**kwargs)
            self.context = context

        def build(self):
            self.title = "Wallet"
            return DashboardLayout(self.context)


def run() -> None:
    """Точка входа GUI-прототипа."""
    if not KIVY_AVAILABLE:
        raise RuntimeError(
            "Kivy не установлен. Установите зависимости: pip install -r requirements.txt"
        )
    # В прототипе используется временная БД в памяти с демонстрационными данными.
    from wallet.core.db import Database

    db = Database()
    db.connect()
    context = AppContext(db)
    context.category_service.ensure_defaults()
    WalletApp(context).run()


if __name__ == "__main__":  # pragma: no cover
    run()
