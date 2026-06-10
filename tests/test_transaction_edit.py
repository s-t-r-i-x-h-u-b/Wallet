"""Тесты редактирования транзакций с пересчётом баланса."""

from __future__ import annotations

from decimal import Decimal

from wallet.models import Transaction, TransactionType


def test_edit_amount_recalculates_balance(context, account):
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("1000"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    context.transaction_service.edit(tx.id, amount=Decimal("600"))
    assert context.accounts.get(account.id).balance == Decimal("600")


def test_edit_can_change_category(context, account):
    from wallet.models import Category, CategoryKind

    food = context.categories.add(Category(name="Еда", kind=CategoryKind.EXPENSE))
    taxi = context.categories.add(Category(name="Такси", kind=CategoryKind.EXPENSE))
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("100"), type=TransactionType.EXPENSE,
                    account_id=account.id, category_id=food.id)
    )
    # смена суммы и категории — одним вызовом сервиса
    context.transaction_service.edit(tx.id, amount=Decimal("150"), category_id=taxi.id)

    result = context.transaction_service.get(tx.id)
    assert result.category_id == taxi.id
    assert result.amount == Decimal("150")


def test_edit_can_clear_category(context, account):
    from wallet.models import Category, CategoryKind

    food = context.categories.add(Category(name="Еда", kind=CategoryKind.EXPENSE))
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("100"), type=TransactionType.EXPENSE,
                    account_id=account.id, category_id=food.id)
    )
    context.transaction_service.edit(tx.id, category_id=None)  # снять категорию
    assert context.transaction_service.get(tx.id).category_id is None


def test_edit_without_category_keeps_it(context, account):
    from wallet.models import Category, CategoryKind

    food = context.categories.add(Category(name="Еда", kind=CategoryKind.EXPENSE))
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("100"), type=TransactionType.EXPENSE,
                    account_id=account.id, category_id=food.id)
    )
    context.transaction_service.edit(tx.id, note="изменено")  # категорию не трогаем
    assert context.transaction_service.get(tx.id).category_id == food.id


def test_edit_type_recalculates_balance(context, account):
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("200"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    # было +200 (доход); меняем на расход -> итог -200
    context.transaction_service.edit(tx.id, tx_type=TransactionType.EXPENSE)
    assert context.accounts.get(account.id).balance == Decimal("-200")
