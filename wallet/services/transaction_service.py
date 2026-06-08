"""Сервис учёта доходов и расходов."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from wallet.models import Transaction, TransactionType
from wallet.repositories import AccountRepository, TransactionRepository


class TransactionService:
    """Добавление, удаление и выборка транзакций с обновлением баланса счёта."""

    def __init__(
        self,
        transactions: TransactionRepository,
        accounts: AccountRepository,
    ):
        self.transactions = transactions
        self.accounts = accounts

    def add(self, transaction: Transaction) -> Transaction:
        if transaction.amount <= 0:
            raise ValueError("Сумма операции должна быть положительной")
        saved = self.transactions.add(transaction)
        self._apply_to_balance(saved, sign=1)
        return saved

    def delete(self, transaction_id: int) -> None:
        tx = self.transactions.get(transaction_id)
        if tx is None:
            return
        self._apply_to_balance(tx, sign=-1)
        self.transactions.delete(transaction_id)

    def list(
        self,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tx_type: Optional[TransactionType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list[Transaction]:
        return self.transactions.list_filtered(
            account_id=account_id,
            category_id=category_id,
            tx_type=tx_type,
            date_from=date_from,
            date_to=date_to,
        )

    def _apply_to_balance(self, tx: Transaction, sign: int) -> None:
        """Изменить баланс счёта: доход увеличивает, расход уменьшает."""
        account = self.accounts.get(tx.account_id)
        if account is None:
            return
        delta = tx.amount if tx.type == TransactionType.INCOME else -tx.amount
        account.balance += Decimal(sign) * delta
        self.accounts.update(account)
