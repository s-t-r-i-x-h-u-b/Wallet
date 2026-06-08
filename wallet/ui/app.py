"""Пользовательский интерфейс на KivyMD (Material Design).

Экран входа открывает зашифрованное хранилище по паролю, далее — нижняя
панель вкладок: Главная, Операции, Цели, Аналитика.

KivyMD/Kivy импортируются «мягко»: если фреймворк не установлен (например,
в среде запуска тестов), модуль остаётся импортируемым, а попытка запустить
GUI сообщает о необходимости установить зависимости.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from pathlib import Path

from wallet.app_context import AppContext
from wallet.core import vault
from wallet.models import CategoryKind, Transaction, TransactionType

DATA_DIR = Path.home() / ".wallet"

try:  # pragma: no cover - наличие GUI зависит от среды
    from kivy.lang import Builder
    from kivy.uix.image import Image  # noqa: F401  (используется в KV)
    from kivymd.app import MDApp
    from kivymd.uix.list import TwoLineListItem
    from kivymd.uix.screen import MDScreen

    KIVYMD_AVAILABLE = True
except Exception:  # noqa: BLE001
    KIVYMD_AVAILABLE = False


if KIVYMD_AVAILABLE:

    KV = """
ScreenManager:
    LoginScreen:
        name: 'login'
    MainScreen:
        name: 'main'

<LoginScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(24)
        spacing: dp(12)
        Widget:
            size_hint_y: None
            height: dp(40)
        MDLabel:
            text: 'Wallet'
            halign: 'center'
            font_style: 'H4'
            size_hint_y: None
            height: dp(60)
        MDLabel:
            text: 'Учёт личных финансов'
            halign: 'center'
            theme_text_color: 'Secondary'
            size_hint_y: None
            height: dp(30)
        MDTextField:
            id: password
            hint_text: 'Пароль'
            password: True
            mode: 'rectangle'
        MDRaisedButton:
            text: 'Войти'
            pos_hint: {'center_x': 0.5}
            on_release: app.login()
        MDFlatButton:
            text: 'Создать хранилище'
            pos_hint: {'center_x': 0.5}
            on_release: app.register()
        MDLabel:
            id: status
            text: ''
            halign: 'center'
            theme_text_color: 'Error'
            size_hint_y: None
            height: dp(30)
        Widget:

<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Wallet'
            right_action_items: [['logout', lambda x: app.logout()]]
        MDBottomNavigation:
            id: nav

            MDBottomNavigationItem:
                name: 'dashboard'
                text: 'Главная'
                icon: 'home'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(16)
                    spacing: dp(8)
                    MDLabel:
                        id: balance
                        text: 'Баланс: —'
                        font_style: 'H5'
                        size_hint_y: None
                        height: dp(50)
                    MDLabel:
                        text: 'Последние операции'
                        theme_text_color: 'Secondary'
                        size_hint_y: None
                        height: dp(28)
                    ScrollView:
                        MDList:
                            id: recent_list

            MDBottomNavigationItem:
                name: 'tx'
                text: 'Операции'
                icon: 'format-list-bulleted'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(16)
                    spacing: dp(6)
                    MDTextField:
                        id: tx_amount
                        hint_text: 'Сумма'
                        input_filter: 'float'
                    MDTextField:
                        id: tx_category
                        hint_text: 'Категория (необязательно)'
                    MDTextField:
                        id: tx_note
                        hint_text: 'Комментарий'
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        MDLabel:
                            text: 'Расход (выкл — доход)'
                        MDSwitch:
                            id: tx_is_expense
                            active: True
                    MDRaisedButton:
                        text: 'Добавить операцию'
                        pos_hint: {'center_x': 0.5}
                        on_release: app.add_transaction()
                    ScrollView:
                        MDList:
                            id: tx_list

            MDBottomNavigationItem:
                name: 'goals'
                text: 'Цели'
                icon: 'target'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(16)
                    spacing: dp(6)
                    MDTextField:
                        id: goal_title
                        hint_text: 'Название цели'
                    MDTextField:
                        id: goal_target
                        hint_text: 'Целевая сумма'
                        input_filter: 'float'
                    MDRaisedButton:
                        text: 'Создать цель'
                        pos_hint: {'center_x': 0.5}
                        on_release: app.add_goal()
                    ScrollView:
                        MDList:
                            id: goals_list

            MDBottomNavigationItem:
                name: 'analytics'
                text: 'Аналитика'
                icon: 'chart-pie'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(16)
                    spacing: dp(8)
                    MDRaisedButton:
                        text: 'Обновить диаграмму'
                        pos_hint: {'center_x': 0.5}
                        on_release: app.build_chart()
                    Image:
                        id: chart_img
"""

    class LoginScreen(MDScreen):
        pass

    class MainScreen(MDScreen):
        pass

    class WalletApp(MDApp):
        """Корневое приложение KivyMD."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.context: AppContext | None = None
            self.account = None

        def build(self):
            self.title = "Wallet"
            self.theme_cls.primary_palette = "Teal"
            self.theme_cls.theme_style = "Light"
            return Builder.load_string(KV)

        # --- вспомогательное ---

        def _login_ids(self):
            return self.root.get_screen("login").ids

        def _main_ids(self):
            return self.root.get_screen("main").ids

        def _toast(self, text: str) -> None:
            try:
                from kivymd.uix.snackbar import Snackbar

                Snackbar(text=text).open()
            except Exception:  # noqa: BLE001
                print(text)

        # --- аутентификация ---

        def register(self):
            password = self._login_ids().password.text
            if not password:
                self._login_ids().status.text = "Введите пароль"
                return
            try:
                self.context = AppContext.init_vault(DATA_DIR, password)
            except FileExistsError:
                self._login_ids().status.text = "Хранилище уже существует — войдите"
                return
            self._enter_app()

        def login(self):
            password = self._login_ids().password.text
            if not vault.vault_exists(DATA_DIR):
                self._login_ids().status.text = "Хранилище не создано — создайте его"
                return
            try:
                self.context = AppContext.open_vault(DATA_DIR, password)
            except vault.InvalidPasswordError:
                self._login_ids().status.text = "Неверный пароль"
                return
            self._enter_app()

        def logout(self):
            if self.context:
                self.context.save()
                self.context.close()
                self.context = None
            self._login_ids().password.text = ""
            self._login_ids().status.text = ""
            self.root.current = "login"

        def _enter_app(self):
            self.context.category_service.ensure_defaults()
            accounts = self.context.account_service.list()
            self.account = accounts[0] if accounts else \
                self.context.account_service.create("Основной счёт")
            self.context.save()
            self._login_ids().status.text = ""
            self.root.current = "main"
            self.refresh_all()

        # --- операции ---

        def _category_id(self, name: str, kind: CategoryKind):
            name = (name or "").strip()
            if not name:
                return None
            for c in self.context.category_service.list():
                if c.name.lower() == name.lower():
                    return c.id
            return self.context.category_service.add(name, kind).id

        def add_transaction(self):
            ids = self._main_ids()
            try:
                amount = Decimal(ids.tx_amount.text)
            except (InvalidOperation, ValueError):
                self._toast("Введите корректную сумму")
                return
            is_expense = ids.tx_is_expense.active
            tx_type = TransactionType.EXPENSE if is_expense else TransactionType.INCOME
            kind = CategoryKind.EXPENSE if is_expense else CategoryKind.INCOME
            try:
                self.context.transaction_service.add(
                    Transaction(
                        amount=amount,
                        type=tx_type,
                        account_id=self.account.id,
                        category_id=self._category_id(ids.tx_category.text, kind),
                        note=ids.tx_note.text,
                    )
                )
            except ValueError as exc:
                self._toast(str(exc))
                return
            self.context.save()
            ids.tx_amount.text = ""
            ids.tx_category.text = ""
            ids.tx_note.text = ""
            self.refresh_all()
            self._toast("Операция добавлена")

        def add_goal(self):
            ids = self._main_ids()
            title = ids.goal_title.text.strip()
            if not title:
                self._toast("Введите название цели")
                return
            try:
                target = Decimal(ids.goal_target.text)
                self.context.goal_service.create(title, target)
            except (InvalidOperation, ValueError):
                self._toast("Введите корректную целевую сумму")
                return
            self.context.save()
            ids.goal_title.text = ""
            ids.goal_target.text = ""
            self.refresh_all()
            self._toast("Цель создана")

        def build_chart(self):
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            path = DATA_DIR / "chart.png"
            self.context.chart_service.expenses_pie(path)
            img = self._main_ids().chart_img
            img.source = str(path)
            img.reload()

        # --- обновление экранов ---

        def refresh_all(self):
            self._refresh_dashboard()
            self._refresh_transactions()
            self._refresh_goals()

        def _refresh_dashboard(self):
            ids = self._main_ids()
            total = self.context.account_service.total_balance()
            ids.balance.text = f"Баланс: {total} ₽"
            ids.recent_list.clear_widgets()
            for tx in self.context.transaction_service.list()[:5]:
                sign = "−" if tx.type == TransactionType.EXPENSE else "+"
                ids.recent_list.add_widget(
                    TwoLineListItem(
                        text=f"{sign}{tx.amount} ₽",
                        secondary_text=tx.note or tx.created_at.strftime("%d.%m.%Y"),
                    )
                )

        def _refresh_transactions(self):
            ids = self._main_ids()
            ids.tx_list.clear_widgets()
            for tx in self.context.transaction_service.list():
                sign = "−" if tx.type == TransactionType.EXPENSE else "+"
                ids.tx_list.add_widget(
                    TwoLineListItem(
                        text=f"{sign}{tx.amount} ₽",
                        secondary_text=(tx.note or "")
                        + "  " + tx.created_at.strftime("%d.%m.%Y"),
                    )
                )

        def _refresh_goals(self):
            ids = self._main_ids()
            ids.goals_list.clear_widgets()
            for goal in self.context.goal_service.list():
                percent = int(goal.progress * 100)
                ids.goals_list.add_widget(
                    TwoLineListItem(
                        text=goal.title,
                        secondary_text=f"{goal.current_amount}/{goal.target_amount} ₽"
                        f" ({percent}%)",
                    )
                )


def run() -> None:
    """Точка входа GUI."""
    if not KIVYMD_AVAILABLE:
        raise RuntimeError(
            "Kivy/KivyMD не установлены. Установите: pip install kivy kivymd"
        )
    WalletApp().run()


if __name__ == "__main__":  # pragma: no cover
    run()
