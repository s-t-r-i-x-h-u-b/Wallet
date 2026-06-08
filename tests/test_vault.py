"""Тесты хранилища с защитой паролем."""

from __future__ import annotations

from decimal import Decimal

import pytest

from wallet.app_context import AppContext
from wallet.core import vault
from wallet.models import Account


def test_init_creates_files(tmp_path):
    vault.init_vault(tmp_path, "pass").close()
    assert (tmp_path / vault.SALT_FILE).exists()
    assert (tmp_path / vault.DB_FILE).exists()
    assert vault.vault_exists(tmp_path)


def test_data_persists_with_correct_password(tmp_path):
    ctx = AppContext.init_vault(tmp_path, "pass")
    ctx.account_service.create("Карта", initial_balance=Decimal("500"))
    ctx.save()
    ctx.close()

    reopened = AppContext.open_vault(tmp_path, "pass")
    accounts = reopened.account_service.list()
    assert [a.name for a in accounts] == ["Карта"]
    assert accounts[0].balance == Decimal("500")


def test_wrong_password_raises(tmp_path):
    vault.init_vault(tmp_path, "right").close()
    with pytest.raises(vault.InvalidPasswordError):
        vault.open_vault(tmp_path, "wrong")


def test_open_missing_vault_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        vault.open_vault(tmp_path / "nope", "pass")
