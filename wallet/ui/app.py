"""Пользовательский интерфейс на KivyMD (Material Design).

Экран входа открывает зашифрованное хранилище по паролю, далее — нижняя
панель вкладок: Главная, Операции, Платежи, Цели, Аналитика.

KivyMD/Kivy импортируются «мягко»: если фреймворк не установлен (например,
в среде запуска тестов), модуль остаётся импортируемым, а попытка запустить
GUI сообщает о необходимости установить зависимости.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from wallet.app_context import AppContext
from wallet.core import vault
from wallet.models import CategoryKind, Reminder, Transaction, TransactionType

NO_CATEGORY = "(без категории)"
PERIOD_MAP = {
    "Ежемесячно": "monthly",
    "Еженедельно": "weekly",
    "Ежедневно": "daily",
    "Ежегодно": "yearly",
}
PERIOD_LABELS = {v: k for k, v in PERIOD_MAP.items()}

try:  # pragma: no cover - наличие GUI зависит от среды
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivy.uix.image import Image  # noqa: F401  (используется в KV)
    from kivy.uix.spinner import Spinner
    from kivymd.app import MDApp
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.button import MDFlatButton, MDRaisedButton
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.list import ThreeLineListItem, TwoLineListItem
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.textfield import MDTextField

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
            left_action_items: [['cog', lambda x: app.open_settings()]]
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
                    padding: dp(12)
                    spacing: dp(6)
                    MDTextField:
                        id: tx_amount
                        hint_text: 'Сумма'
                        input_filter: 'float'
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        Spinner:
                            id: tx_type
                            text: 'Расход'
                            values: ['Расход', 'Доход']
                        Spinner:
                            id: tx_category
                            text: 'Категория'
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        MDFlatButton:
                            text: 'Добавить категорию'
                            on_release: app.open_add_category()
                        MDFlatButton:
                            text: 'Удалить категорию'
                            theme_text_color: 'Custom'
                            text_color: 0.8, 0.2, 0.2, 1
                            on_release: app.open_delete_category()
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        MDFlatButton:
                            id: tx_date_btn
                            text: 'Дата: сегодня'
                            on_release: app.open_tx_date_picker()
                        MDTextField:
                            id: tx_note
                            hint_text: 'Комментарий'
                    MDRaisedButton:
                        text: 'Добавить операцию'
                        pos_hint: {'center_x': 0.5}
                        on_release: app.add_transaction()
                    MDLabel:
                        text: 'История операций'
                        theme_text_color: 'Secondary'
                        size_hint_y: None
                        height: dp(26)
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        Spinner:
                            id: flt_type
                            text: 'Все'
                            values: ['Все', 'Доход', 'Расход']
                            on_text: app.apply_filter()
                        Spinner:
                            id: flt_category
                            text: 'Все'
                            on_text: app.apply_filter()
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        MDFlatButton:
                            id: flt_from_btn
                            text: 'С: —'
                            on_release: app.open_flt_from()
                        MDFlatButton:
                            id: flt_to_btn
                            text: 'По: —'
                            on_release: app.open_flt_to()
                        MDFlatButton:
                            text: 'Сброс'
                            on_release: app.reset_flt()
                    MDLabel:
                        text: 'Нажмите на операцию, чтобы изменить или удалить'
                        theme_text_color: 'Secondary'
                        font_style: 'Caption'
                        size_hint_y: None
                        height: dp(26)
                    ScrollView:
                        MDList:
                            id: tx_list

            MDBottomNavigationItem:
                name: 'payments'
                text: 'Платежи'
                icon: 'calendar-clock'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(12)
                    spacing: dp(6)
                    MDTextField:
                        id: rem_title
                        hint_text: 'Название платежа'
                    MDTextField:
                        id: rem_amount
                        hint_text: 'Сумма'
                        input_filter: 'float'
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        MDFlatButton:
                            id: rem_date_btn
                            text: 'Срок: сегодня'
                            on_release: app.open_rem_date_picker()
                        Spinner:
                            id: rem_period
                            text: 'Разовый'
                            values: ['Разовый', 'Ежемесячно', 'Еженедельно', 'Ежедневно', 'Ежегодно']
                    MDRaisedButton:
                        text: 'Добавить платёж'
                        pos_hint: {'center_x': 0.5}
                        on_release: app.add_reminder()
                    MDLabel:
                        text: 'Нажмите на платёж, чтобы изменить, оплатить/перенести или удалить'
                        theme_text_color: 'Secondary'
                        font_style: 'Caption'
                        size_hint_y: None
                        height: dp(28)
                    ScrollView:
                        MDList:
                            id: rem_list

            MDBottomNavigationItem:
                name: 'goals'
                text: 'Цели'
                icon: 'target'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(12)
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
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        Spinner:
                            id: goal_select
                            text: 'Цель'
                        MDTextField:
                            id: goal_amount
                            hint_text: 'Сумма пополнения'
                            input_filter: 'float'
                        MDRaisedButton:
                            text: 'Пополнить'
                            size_hint_x: None
                            width: dp(120)
                            on_release: app.contribute_goal()
                    MDLabel:
                        text: 'Нажмите на цель, чтобы изменить или удалить'
                        theme_text_color: 'Secondary'
                        font_style: 'Caption'
                        size_hint_y: None
                        height: dp(28)
                    ScrollView:
                        MDList:
                            id: goals_list

            MDBottomNavigationItem:
                name: 'analytics'
                text: 'Аналитика'
                icon: 'chart-pie'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(12)
                    spacing: dp(8)
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        MDFlatButton:
                            id: an_from_btn
                            text: 'С: —'
                            on_release: app.open_an_from()
                        MDFlatButton:
                            id: an_to_btn
                            text: 'По: —'
                            on_release: app.open_an_to()
                        MDFlatButton:
                            text: 'Сброс'
                            on_release: app.reset_an()
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(8)
                        MDRaisedButton:
                            text: 'Расходы по категориям'
                            on_release: app.build_pie()
                        MDRaisedButton:
                            text: 'Динамика по месяцам'
                            on_release: app.build_dynamics()
                    Image:
                        id: chart_img
"""

    class LoginScreen(MDScreen):
        pass

    class MainScreen(MDScreen):
        pass

    class _EditContent(MDBoxLayout):
        """Содержимое диалога редактирования с произвольным числом полей."""

        def __init__(self, *widgets, **kwargs):
            super().__init__(orientation="vertical", spacing=dp(8),
                             padding=dp(8), size_hint_y=None, **kwargs)
            self.fields = list(widgets)
            self.height = dp(64) * len(widgets) + dp(16)
            for widget in widgets:
                self.add_widget(widget)

    class WalletApp(MDApp):
        """Корневое приложение KivyMD."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.context: AppContext | None = None
            self.account = None
            self.tx_date = date.today()
            self.rem_date = date.today()
            self._dialog = None
            self._confirm = None         # диалог подтверждения удаления
            self._edit_due = None       # дата срока при редактировании платежа
            self._edit_due_btn = None
            self.flt_from = None         # фильтр истории: начало периода
            self.flt_to = None           # фильтр истории: конец периода
            self.an_from = None          # аналитика: начало периода
            self.an_to = None            # аналитика: конец периода

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

        def _data_dir(self) -> Path:
            """Каталог данных приложения (приватный, зависит от платформы)."""
            base = Path(self.user_data_dir)
            base.mkdir(parents=True, exist_ok=True)
            return base

        def _toast(self, text: str) -> None:
            try:
                from kivymd.uix.snackbar import Snackbar

                Snackbar(text=text).open()
            except Exception:  # noqa: BLE001
                print(text)

        def _confirm_delete(self, message: str, on_confirm) -> None:
            """Показать диалог подтверждения удаления."""
            self._confirm = MDDialog(
                title="Подтверждение",
                text=message,
                buttons=[
                    MDFlatButton(text="Отмена",
                                 on_release=lambda *_: self._confirm.dismiss()),
                    MDRaisedButton(text="Удалить", md_bg_color=(0.8, 0.2, 0.2, 1),
                                   on_release=lambda *_: self._run_confirmed(on_confirm)),
                ],
            )
            self._confirm.open()

        def _run_confirmed(self, on_confirm) -> None:
            self._confirm.dismiss()
            on_confirm()

        def _categories(self):
            return self.context.category_service.list()

        def _category_by_name(self, name: str):
            for c in self._categories():
                if c.name == name:
                    return c
            return None

        def _cat_name(self, category_id):
            if category_id is None:
                return ""
            for c in self._categories():
                if c.id == category_id:
                    return c.name
            return ""

        # --- аутентификация ---

        def register(self):
            password = self._login_ids().password.text
            if not password:
                self._login_ids().status.text = "Введите пароль"
                return
            try:
                self.context = AppContext.init_vault(self._data_dir(), password)
            except FileExistsError:
                self._login_ids().status.text = "Хранилище уже существует — войдите"
                return
            self._enter_app()

        def login(self):
            password = self._login_ids().password.text
            if not vault.vault_exists(self._data_dir()):
                self._login_ids().status.text = "Хранилище не создано — создайте его"
                return
            try:
                self.context = AppContext.open_vault(self._data_dir(), password)
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
            self.tx_date = date.today()
            self.rem_date = date.today()
            self._login_ids().status.text = ""
            self.root.current = "main"
            ids = self._main_ids()
            ids.tx_date_btn.text = f"Дата: {self.tx_date.strftime('%d.%m.%Y')}"
            ids.rem_date_btn.text = f"Срок: {self.rem_date.strftime('%d.%m.%Y')}"
            self.refresh_all()
            self._notify_due_payments()

        def _notify_due_payments(self):
            """Разослать уведомления о наступивших платежах при входе.

            Ошибки backend уведомлений (например, в среде без графической
            оболочки) не должны мешать работе приложения.
            """
            try:
                self.context.reminder_service.notify_due(self.context.notifier)
            except Exception:  # noqa: BLE001
                pass

        # --- выбор даты ---

        def open_tx_date_picker(self):
            from kivymd.uix.pickers import MDDatePicker

            picker = MDDatePicker()
            picker.bind(on_save=self._on_tx_date_save)
            picker.open()

        def _on_tx_date_save(self, instance, value, date_range):
            self.tx_date = value
            self._main_ids().tx_date_btn.text = f"Дата: {value.strftime('%d.%m.%Y')}"

        def open_rem_date_picker(self):
            from kivymd.uix.pickers import MDDatePicker

            picker = MDDatePicker()
            picker.bind(on_save=self._on_rem_date_save)
            picker.open()

        def _on_rem_date_save(self, instance, value, date_range):
            self.rem_date = value
            self._main_ids().rem_date_btn.text = f"Срок: {value.strftime('%d.%m.%Y')}"

        # --- категории ---

        def _resolve_category(self, name: str, kind: CategoryKind):
            name = (name or "").strip()
            if not name or name in (NO_CATEGORY, "Категория"):
                return None
            existing = self._category_by_name(name)
            if existing:
                return existing.id
            return self.context.category_service.add(name, kind).id

        def open_add_category(self):
            content = _EditContent(MDTextField(hint_text="Название категории"))
            self._dialog = MDDialog(
                title="Новая категория",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text="Отмена",
                                 on_release=lambda *_: self._dialog.dismiss()),
                    MDRaisedButton(text="Создать",
                                   on_release=lambda *_: self._create_category(content)),
                ],
            )
            self._dialog.open()

        def _create_category(self, content):
            name = content.fields[0].text.strip()
            if not name:
                self._toast("Введите название категории")
                return
            ids = self._main_ids()
            kind = (CategoryKind.EXPENSE if ids.tx_type.text == "Расход"
                    else CategoryKind.INCOME)
            if self._category_by_name(name) is None:
                self.context.category_service.add(name, kind)
                self.context.save()
            self._dialog.dismiss()
            self._populate_spinners()
            ids.tx_category.text = name
            self._toast("Категория добавлена")

        def open_delete_category(self):
            names = [c.name for c in self._categories()]
            if not names:
                self._toast("Нет категорий для удаления")
                return
            content = _EditContent(
                Spinner(text=names[0], values=names, size_hint_y=None, height=dp(44)),
            )
            self._dialog = MDDialog(
                title="Удалить категорию",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text="Отмена",
                                 on_release=lambda *_: self._dialog.dismiss()),
                    MDRaisedButton(text="Удалить", md_bg_color=(0.8, 0.2, 0.2, 1),
                                   on_release=lambda *_: self._ask_remove_category(content)),
                ],
            )
            self._dialog.open()

        def _ask_remove_category(self, content):
            name = content.fields[0].text
            category = self._category_by_name(name)
            if category is None:
                self._toast("Категория не найдена")
                return
            self._dialog.dismiss()
            self._confirm_delete(
                f"Удалить категорию «{name}»?",
                lambda: self._remove_category_confirmed(category.id, name),
            )

        def _remove_category_confirmed(self, category_id, name):
            self.context.category_service.delete(category_id)
            self.context.save()
            if self._main_ids().tx_category.text == name:
                self._main_ids().tx_category.text = NO_CATEGORY
            self._populate_spinners()
            self.refresh_all()
            self._toast("Категория удалена")

        # --- выбор диапазона дат ---

        def _pick(self, callback):
            from kivymd.uix.pickers import MDDatePicker

            picker = MDDatePicker()
            picker.bind(on_save=lambda inst, value, rng: callback(value))
            picker.open()

        @staticmethod
        def _day_start(d):
            return datetime.combine(d, datetime.min.time()) if d else None

        @staticmethod
        def _day_end(d):
            return datetime.combine(d, datetime.max.time()) if d else None

        def open_flt_from(self):
            self._pick(self._set_flt_from)

        def open_flt_to(self):
            self._pick(self._set_flt_to)

        def _set_flt_from(self, value):
            self.flt_from = value
            self._main_ids().flt_from_btn.text = f"С: {value.strftime('%d.%m.%Y')}"
            self._refresh_transactions()

        def _set_flt_to(self, value):
            self.flt_to = value
            self._main_ids().flt_to_btn.text = f"По: {value.strftime('%d.%m.%Y')}"
            self._refresh_transactions()

        def reset_flt(self):
            self.flt_from = self.flt_to = None
            ids = self._main_ids()
            ids.flt_from_btn.text = "С: —"
            ids.flt_to_btn.text = "По: —"
            self._refresh_transactions()

        def open_an_from(self):
            self._pick(self._set_an_from)

        def open_an_to(self):
            self._pick(self._set_an_to)

        def _set_an_from(self, value):
            self.an_from = value
            self._main_ids().an_from_btn.text = f"С: {value.strftime('%d.%m.%Y')}"

        def _set_an_to(self, value):
            self.an_to = value
            self._main_ids().an_to_btn.text = f"По: {value.strftime('%d.%m.%Y')}"

        def reset_an(self):
            self.an_from = self.an_to = None
            ids = self._main_ids()
            ids.an_from_btn.text = "С: —"
            ids.an_to_btn.text = "По: —"

        def _set_edit_due(self, value):
            self._edit_due = value
            if self._edit_due_btn is not None:
                self._edit_due_btn.text = f"Срок: {value.strftime('%d.%m.%Y')}"

        # --- настройки ---

        def open_settings(self):
            if not self.context:
                return
            content = _EditContent(
                MDTextField(hint_text="Новый пароль", password=True),
                MDTextField(hint_text="Повторите пароль", password=True),
            )
            self._dialog = MDDialog(
                title="Настройки — смена пароля",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text="Отмена",
                                 on_release=lambda *_: self._dialog.dismiss()),
                    MDRaisedButton(text="Сохранить",
                                   on_release=lambda *_: self._save_settings(content)),
                ],
            )
            self._dialog.open()

        def _save_settings(self, content):
            new_pwd = content.fields[0].text
            confirm = content.fields[1].text
            if not new_pwd:
                self._toast("Пароль не может быть пустым")
                return
            if new_pwd != confirm:
                self._toast("Пароли не совпадают")
                return
            self.context.change_password(new_pwd)
            self._dialog.dismiss()
            self._toast("Пароль изменён")

        # --- операции ---

        def add_transaction(self):
            ids = self._main_ids()
            try:
                amount = Decimal(ids.tx_amount.text)
            except (InvalidOperation, ValueError):
                self._toast("Введите корректную сумму")
                return
            is_expense = ids.tx_type.text == "Расход"
            tx_type = TransactionType.EXPENSE if is_expense else TransactionType.INCOME
            kind = CategoryKind.EXPENSE if is_expense else CategoryKind.INCOME
            created_at = datetime.combine(self.tx_date, datetime.now().time())
            try:
                self.context.transaction_service.add(
                    Transaction(
                        amount=amount,
                        type=tx_type,
                        account_id=self.account.id,
                        category_id=self._resolve_category(ids.tx_category.text, kind),
                        note=ids.tx_note.text,
                        created_at=created_at,
                    )
                )
            except ValueError as exc:
                self._toast(str(exc))
                return
            self.context.save()
            ids.tx_amount.text = ""
            ids.tx_note.text = ""
            self.tx_date = date.today()
            ids.tx_date_btn.text = f"Дата: {self.tx_date.strftime('%d.%m.%Y')}"
            self.refresh_all()
            self._toast("Операция добавлена")

        def apply_filter(self):
            if not self.context:
                return
            self._refresh_transactions()

        def open_tx_dialog(self, tx_id):
            tx = self.context.transactions.get(tx_id)
            if tx is None:
                return
            names = [c.name for c in self._categories()]
            content = _EditContent(
                MDTextField(text=str(tx.amount), hint_text="Сумма",
                            input_filter="float"),
                Spinner(text="Расход" if tx.type == TransactionType.EXPENSE else "Доход",
                        values=["Расход", "Доход"], size_hint_y=None, height=dp(44)),
                Spinner(text=self._cat_name(tx.category_id) or NO_CATEGORY,
                        values=[NO_CATEGORY] + names, size_hint_y=None, height=dp(44)),
                MDTextField(text=tx.note, hint_text="Комментарий"),
            )
            self._dialog = MDDialog(
                title="Операция",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text="Удалить", theme_text_color="Custom",
                                 text_color=(0.8, 0.1, 0.1, 1),
                                 on_release=lambda *_: self._ask_delete_tx(tx_id)),
                    MDFlatButton(text="Отмена",
                                 on_release=lambda *_: self._dialog.dismiss()),
                    MDRaisedButton(text="Сохранить",
                                   on_release=lambda *_: self._save_tx(tx_id, content)),
                ],
            )
            self._dialog.open()

        def _save_tx(self, tx_id, content):
            try:
                amount = Decimal(content.fields[0].text)
            except (InvalidOperation, ValueError):
                self._toast("Некорректная сумма")
                return
            is_expense = content.fields[1].text == "Расход"
            tx_type = TransactionType.EXPENSE if is_expense else TransactionType.INCOME
            kind = CategoryKind.EXPENSE if is_expense else CategoryKind.INCOME
            category_id = self._resolve_category(content.fields[2].text, kind)
            note = content.fields[3].text
            try:
                tx = self.context.transaction_service.edit(
                    tx_id, amount=amount, note=note, tx_type=tx_type)
            except ValueError as exc:
                self._toast(str(exc))
                return
            tx.category_id = category_id  # категория может быть снята (None)
            self.context.transactions.update(tx)
            self.context.save()
            self._dialog.dismiss()
            self.refresh_all()
            self._toast("Операция изменена")

        def _ask_delete_tx(self, tx_id):
            self._dialog.dismiss()
            self._confirm_delete("Удалить операцию?",
                                 lambda: self._delete_tx(tx_id))

        def _delete_tx(self, tx_id):
            self.context.transaction_service.delete(tx_id)
            self.context.save()
            self.refresh_all()
            self._toast("Операция удалена")

        # --- цели ---

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

        def contribute_goal(self):
            ids = self._main_ids()
            title = ids.goal_select.text
            goal = next((g for g in self.context.goal_service.list()
                         if g.title == title), None)
            if goal is None:
                self._toast("Выберите цель")
                return
            try:
                amount = Decimal(ids.goal_amount.text)
                self.context.goal_service.contribute(goal.id, amount)
            except (InvalidOperation, ValueError) as exc:
                self._toast("Введите корректную сумму пополнения"
                            if isinstance(exc, InvalidOperation) else str(exc))
                return
            self.context.save()
            ids.goal_amount.text = ""
            self.refresh_all()
            self._toast("Цель пополнена")

        def open_goal_dialog(self, goal_id):
            goal = self.context.goals.get(goal_id)
            if goal is None:
                return
            content = _EditContent(
                MDTextField(text=goal.title, hint_text="Название цели"),
                MDTextField(text=str(goal.target_amount), hint_text="Целевая сумма",
                            input_filter="float"),
            )
            self._dialog = MDDialog(
                title="Редактирование цели",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text="Удалить", theme_text_color="Custom",
                                 text_color=(0.8, 0.1, 0.1, 1),
                                 on_release=lambda *_: self._ask_delete_goal(goal_id)),
                    MDFlatButton(text="Отмена",
                                 on_release=lambda *_: self._dialog.dismiss()),
                    MDRaisedButton(text="Сохранить",
                                   on_release=lambda *_: self._save_goal(goal_id, content)),
                ],
            )
            self._dialog.open()

        def _save_goal(self, goal_id, content):
            try:
                target = Decimal(content.fields[1].text)
            except (InvalidOperation, ValueError):
                self._toast("Некорректная целевая сумма")
                return
            try:
                self.context.goal_service.update(
                    goal_id, title=content.fields[0].text, target_amount=target)
            except ValueError as exc:
                self._toast(str(exc))
                return
            self.context.save()
            self._dialog.dismiss()
            self.refresh_all()
            self._toast("Цель обновлена")

        def _ask_delete_goal(self, goal_id):
            self._dialog.dismiss()
            self._confirm_delete("Удалить цель?",
                                 lambda: self._delete_goal(goal_id))

        def _delete_goal(self, goal_id):
            self.context.goal_service.delete(goal_id)
            self.context.save()
            self.refresh_all()
            self._toast("Цель удалена")

        # --- платежи (напоминания) ---

        def add_reminder(self):
            ids = self._main_ids()
            title = ids.rem_title.text.strip()
            if not title:
                self._toast("Введите название платежа")
                return
            try:
                amount = Decimal(ids.rem_amount.text)
            except (InvalidOperation, ValueError):
                self._toast("Введите корректную сумму")
                return
            period = PERIOD_MAP.get(ids.rem_period.text, "")
            try:
                self.context.reminder_service.schedule(
                    Reminder(
                        title=title,
                        amount=amount,
                        due_date=self.rem_date,
                        is_repeating=bool(period),
                        period=period,
                    )
                )
            except ValueError as exc:
                self._toast(str(exc))
                return
            self.context.save()
            ids.rem_title.text = ""
            ids.rem_amount.text = ""
            self.rem_date = date.today()
            ids.rem_date_btn.text = f"Срок: {self.rem_date.strftime('%d.%m.%Y')}"
            self.refresh_all()
            self._toast("Платёж добавлен")

        def pay_reminder(self, reminder_id: int, repeating: bool):
            if repeating:
                self.context.reminder_service.advance(reminder_id)
                self._toast("Платёж перенесён на следующий период")
            else:
                self.context.reminder_service.delete(reminder_id)
                self._toast("Платёж отмечен оплаченным")
            self.context.save()
            self.refresh_all()

        def open_reminder_dialog(self, reminder_id, repeating):
            reminder = self.context.reminders.get(reminder_id)
            if reminder is None:
                return
            period_spinner = Spinner(
                text=PERIOD_LABELS.get(reminder.period, "Разовый"),
                values=["Разовый"] + list(PERIOD_MAP.keys()),
                size_hint_y=None, height=dp(44),
            )
            self._edit_due = reminder.due_date
            self._edit_due_btn = MDFlatButton(
                text=f"Срок: {reminder.due_date.strftime('%d.%m.%Y')}")
            self._edit_due_btn.bind(
                on_release=lambda *_: self._pick(self._set_edit_due))
            content = _EditContent(
                MDTextField(text=reminder.title, hint_text="Название платежа"),
                MDTextField(text=str(reminder.amount), hint_text="Сумма",
                            input_filter="float"),
                period_spinner,
                self._edit_due_btn,
            )
            pay_label = "Перенести" if repeating else "Оплатить"
            self._dialog = MDDialog(
                title="Платёж",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(text=pay_label,
                                 on_release=lambda *_: self._pay_from_dialog(
                                     reminder_id, repeating)),
                    MDFlatButton(text="Удалить", theme_text_color="Custom",
                                 text_color=(0.8, 0.1, 0.1, 1),
                                 on_release=lambda *_: self._ask_delete_reminder(reminder_id)),
                    MDRaisedButton(text="Сохранить",
                                   on_release=lambda *_: self._save_reminder(
                                       reminder_id, content)),
                ],
            )
            self._dialog.open()

        def _pay_from_dialog(self, reminder_id, repeating):
            self._dialog.dismiss()
            self.pay_reminder(reminder_id, repeating)

        def _save_reminder(self, reminder_id, content):
            try:
                amount = Decimal(content.fields[1].text)
            except (InvalidOperation, ValueError):
                self._toast("Некорректная сумма")
                return
            period = PERIOD_MAP.get(content.fields[2].text, "")
            try:
                self.context.reminder_service.update(
                    reminder_id, title=content.fields[0].text, amount=amount,
                    period=period, due_date=self._edit_due)
            except ValueError as exc:
                self._toast(str(exc))
                return
            self.context.save()
            self._dialog.dismiss()
            self.refresh_all()
            self._toast("Платёж обновлён")

        def _ask_delete_reminder(self, reminder_id):
            self._dialog.dismiss()
            self._confirm_delete("Удалить платёж?",
                                 lambda: self._delete_reminder(reminder_id))

        def _delete_reminder(self, reminder_id):
            self.context.reminder_service.delete(reminder_id)
            self.context.save()
            self.refresh_all()
            self._toast("Платёж удалён")

        # --- аналитика ---

        def build_pie(self):
            path = self._data_dir() / "chart_pie.png"
            try:
                self.context.chart_service.expenses_pie(
                    path, self._day_start(self.an_from), self._day_end(self.an_to))
            except ImportError:
                self._toast("Диаграммы недоступны: не установлен matplotlib")
                return
            self._set_chart(path)

        def build_dynamics(self):
            path = self._data_dir() / "chart_dyn.png"
            try:
                self.context.chart_service.dynamics_chart(
                    path, self._day_start(self.an_from), self._day_end(self.an_to))
            except ImportError:
                self._toast("Диаграммы недоступны: не установлен matplotlib")
                return
            self._set_chart(path)

        def _set_chart(self, path):
            img = self._main_ids().chart_img
            img.source = str(path)
            img.reload()

        # --- обновление экранов ---

        def refresh_all(self):
            if not self.context:
                return
            self._populate_spinners()
            self._refresh_dashboard()
            self._refresh_transactions()
            self._refresh_goals()
            self._refresh_reminders()

        def _populate_spinners(self):
            ids = self._main_ids()
            names = [c.name for c in self._categories()]
            ids.tx_category.values = [NO_CATEGORY] + names
            if ids.tx_category.text in ("Категория", ""):
                ids.tx_category.text = NO_CATEGORY
            ids.flt_category.values = ["Все"] + names
            goals = [g.title for g in self.context.goal_service.list()]
            ids.goal_select.values = goals
            if goals and ids.goal_select.text in ("Цель", ""):
                ids.goal_select.text = goals[0]

        def _tx_item(self, tx):
            sign = "−" if tx.type == TransactionType.EXPENSE else "+"
            category = self._cat_name(tx.category_id) or "без категории"
            item = ThreeLineListItem(
                text=f"{sign}{tx.amount} ₽",
                secondary_text=f"{tx.created_at.strftime('%d.%m.%Y')} · {category}",
                tertiary_text=tx.note or "—",
            )
            item.bind(on_release=lambda inst, tid=tx.id: self.open_tx_dialog(tid))
            return item

        def _refresh_dashboard(self):
            ids = self._main_ids()
            total = self.context.account_service.total_balance()
            ids.balance.text = f"Баланс: {total} ₽"
            ids.recent_list.clear_widgets()
            for tx in self.context.transaction_service.list()[:5]:
                ids.recent_list.add_widget(self._tx_item(tx))

        def _refresh_transactions(self):
            ids = self._main_ids()
            tx_type = None
            if ids.flt_type.text == "Доход":
                tx_type = TransactionType.INCOME
            elif ids.flt_type.text == "Расход":
                tx_type = TransactionType.EXPENSE
            category_id = None
            if ids.flt_category.text not in ("Все", ""):
                cat = self._category_by_name(ids.flt_category.text)
                category_id = cat.id if cat else -1
            ids.tx_list.clear_widgets()
            for tx in self.context.transaction_service.list(
                category_id=category_id, tx_type=tx_type,
                date_from=self._day_start(self.flt_from),
                date_to=self._day_end(self.flt_to),
            ):
                ids.tx_list.add_widget(self._tx_item(tx))

        def _refresh_goals(self):
            ids = self._main_ids()
            ids.goals_list.clear_widgets()
            for goal in self.context.goal_service.list():
                percent = int(goal.progress * 100)
                status = " (выполнена)" if goal.is_reached else ""
                item = TwoLineListItem(
                    text=f"{goal.title}{status}",
                    secondary_text=f"{goal.current_amount}/{goal.target_amount} ₽"
                    f" ({percent}%)",
                )
                item.bind(on_release=lambda inst, gid=goal.id:
                          self.open_goal_dialog(gid))
                ids.goals_list.add_widget(item)

        def _refresh_reminders(self):
            ids = self._main_ids()
            ids.rem_list.clear_widgets()
            for r in sorted(self.context.reminder_service.list(),
                            key=lambda x: x.due_date):
                period = PERIOD_LABELS.get(r.period, "разовый")
                item = TwoLineListItem(
                    text=f"{r.title} — {r.amount} ₽",
                    secondary_text=f"срок {r.due_date.strftime('%d.%m.%Y')} · {period}",
                )
                item.bind(
                    on_release=lambda inst, rid=r.id, rep=r.is_repeating:
                    self.open_reminder_dialog(rid, rep)
                )
                ids.rem_list.add_widget(item)


def run() -> None:
    """Точка входа GUI."""
    if not KIVYMD_AVAILABLE:
        raise RuntimeError(
            "Kivy/KivyMD не установлены. Установите: pip install kivy kivymd"
        )
    WalletApp().run()


if __name__ == "__main__":  # pragma: no cover
    run()
