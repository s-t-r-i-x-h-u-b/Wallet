"""Сервис управления категориями."""

from __future__ import annotations

from wallet.models import Category, CategoryKind
from wallet.repositories import CategoryRepository

DEFAULT_CATEGORIES: list[tuple[str, CategoryKind]] = [
    ("Продукты", CategoryKind.EXPENSE),
    ("Транспорт", CategoryKind.EXPENSE),
    ("Жильё", CategoryKind.EXPENSE),
    ("Развлечения", CategoryKind.EXPENSE),
    ("Здоровье", CategoryKind.EXPENSE),
    ("Зарплата", CategoryKind.INCOME),
    ("Прочие доходы", CategoryKind.INCOME),
]


class CategoryService:
    """Создание пользовательских и предопределённых категорий."""

    def __init__(self, categories: CategoryRepository):
        self.categories = categories

    def add(self, name: str, kind: CategoryKind, icon: str = "") -> Category:
        if not name:
            raise ValueError("Название категории не может быть пустым")
        return self.categories.add(Category(name=name, kind=kind, icon=icon))

    def list(self) -> list[Category]:
        return self.categories.list()

    def delete(self, category_id: int) -> None:
        """Удалить категорию, обнулив ссылки на неё у операций и платежей."""
        conn = self.categories.conn
        conn.execute(
            "UPDATE transactions SET category_id = NULL WHERE category_id = ?",
            (category_id,),
        )
        conn.execute(
            "UPDATE reminders SET category_id = NULL WHERE category_id = ?",
            (category_id,),
        )
        self.categories.delete(category_id)

    def ensure_defaults(self) -> list[Category]:
        """Создать предопределённые категории, если их ещё нет."""
        existing = {c.name for c in self.categories.list()}
        created: list[Category] = []
        for name, kind in DEFAULT_CATEGORIES:
            if name not in existing:
                created.append(
                    self.categories.add(
                        Category(name=name, kind=kind, is_predefined=True)
                    )
                )
        return created
