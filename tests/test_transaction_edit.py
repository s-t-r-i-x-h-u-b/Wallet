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


def test_edit_type_recalculates_balance(context, account):
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("200"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    # было +200 (доход); меняем на расход -> итог -200
    context.transaction_service.edit(tx.id, tx_type=TransactionType.EXPENSE)
    assert context.accounts.get(account.id).balance == Decimal("-200")
