"""Тесты сервиса учёта доходов и расходов."""

from __future__ import annotations

from decimal import Decimal

import pytest

from wallet.models import Transaction, TransactionType


def test_income_increases_balance(context, account):
    context.transaction_service.add(
        Transaction(amount=Decimal("1000"), type=TransactionType.INCOME,
                    account_id=account.id, note="Зарплата")
    )
    assert context.accounts.get(account.id).balance == Decimal("1000")


def test_expense_decreases_balance(context, account):
    context.transaction_service.add(
        Transaction(amount=Decimal("1000"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    context.transaction_service.add(
        Transaction(amount=Decimal("300"), type=TransactionType.EXPENSE,
                    account_id=account.id, note="Продукты")
    )
    assert context.accounts.get(account.id).balance == Decimal("700")


def test_negative_amount_rejected(context, account):
    with pytest.raises(ValueError):
        context.transaction_service.add(
            Transaction(amount=Decimal("-5"), type=TransactionType.EXPENSE,
                        account_id=account.id)
        )


def test_delete_reverts_balance(context, account):
    tx = context.transaction_service.add(
        Transaction(amount=Decimal("500"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    context.transaction_service.delete(tx.id)
    assert context.accounts.get(account.id).balance == Decimal("0")
    assert context.transaction_service.list(account_id=account.id) == []


def test_filter_by_type(context, account):
    context.transaction_service.add(
        Transaction(amount=Decimal("100"), type=TransactionType.INCOME,
                    account_id=account.id)
    )
    context.transaction_service.add(
        Transaction(amount=Decimal("40"), type=TransactionType.EXPENSE,
                    account_id=account.id)
    )
    expenses = context.transaction_service.list(tx_type=TransactionType.EXPENSE)
    assert len(expenses) == 1
    assert expenses[0].amount == Decimal("40")
