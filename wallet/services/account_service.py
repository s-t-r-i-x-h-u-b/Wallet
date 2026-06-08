"""Сервис управления счетами."""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from wallet.models import Account
from wallet.repositories import AccountRepository


class AccountService:
    """Создание счетов и получение сводной информации по балансу."""

    def __init__(self, accounts: AccountRepository):
        self.accounts = accounts

    def create(
        self,
        name: str,
        type: str = "cash",
        currency: str = "RUB",
        initial_balance: Decimal = Decimal("0"),
        user_id: Optional[int] = None,
    ) -> Account:
        if not name:
            raise ValueError("Название счёта не может быть пустым")
        return self.accounts.add(
            Account(
                name=name,
                type=type,
                balance=initial_balance,
                currency=currency,
                user_id=user_id,
            )
        )

    def list(self) -> list[Account]:
        return self.accounts.list()

    def total_balance(self) -> Decimal:
        """Суммарный баланс по всем счетам."""
        return sum((a.balance for a in self.accounts.list()), Decimal("0"))
