"""Тесты сервиса счетов."""

from __future__ import annotations

from decimal import Decimal

import pytest


def test_create_account(context):
    acc = context.account_service.create("Карта", type="card",
                                         initial_balance=Decimal("100"))
    assert acc.id is not None
    assert acc.balance == Decimal("100")


def test_empty_name_rejected(context):
    with pytest.raises(ValueError):
        context.account_service.create("")


def test_total_balance(context):
    context.account_service.create("Наличные", initial_balance=Decimal("300"))
    context.account_service.create("Карта", initial_balance=Decimal("700"))
    assert context.account_service.total_balance() == Decimal("1000")
