"""Тесты сервиса категорий."""

from __future__ import annotations

from decimal import Decimal

from wallet.models import Category, CategoryKind, Transaction, TransactionType


def test_ensure_defaults_creates_predefined(context):
    created = context.category_service.ensure_defaults()
    assert len(created) > 0
    # повторный вызов не дублирует
    assert context.category_service.ensure_defaults() == []


def test_add_custom_category(context):
    cat = context.category_service.add("Кафе", CategoryKind.EXPENSE)
    assert cat.id is not None
    assert any(c.name == "Кафе" for c in context.category_service.list())


def test_delete_category_nullifies_transactions(context, account):
    cat = context.category_service.add("Такси", CategoryKind.EXPENSE)
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("300"), type=TransactionType.EXPENSE,
                    account_id=account.id, category_id=cat.id)
    )
    context.category_service.delete(cat.id)
    assert all(c.id != cat.id for c in context.category_service.list())
    # операция сохранилась, но без категории
    assert context.transactions.get(tx.id).category_id is None
