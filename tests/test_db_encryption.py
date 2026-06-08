"""Тесты шифрования базы данных «в покое»."""

from __future__ import annotations

from decimal import Decimal

import pytest

from wallet.core.db import Database
from wallet.core.security import EncryptionManager, derive_key
from wallet.models import Account
from wallet.repositories import AccountRepository

SALT = b"fixed-salt-16byte"


def _manager(password: str) -> EncryptionManager:
    return EncryptionManager(derive_key(password, SALT))


def test_data_persists_through_encrypted_file(tmp_path):
    path = tmp_path / "wallet.db.enc"

    db = Database(path=path, encryption=_manager("pass"))
    db.connect()
    AccountRepository(db.connection).add(
        Account(name="Карта", type="card", balance=Decimal("100.50"))
    )
    db.save()
    db.close()

    assert path.exists()

    db2 = Database(path=path, encryption=_manager("pass"))
    db2.connect()
    accounts = AccountRepository(db2.connection).list()
    assert len(accounts) == 1
    assert accounts[0].name == "Карта"
    assert accounts[0].balance == Decimal("100.50")


def test_file_is_not_plaintext(tmp_path):
    path = tmp_path / "wallet.db.enc"
    db = Database(path=path, encryption=_manager("pass"))
    db.connect()
    AccountRepository(db.connection).add(Account(name="SecretAccount"))
    db.save()
    db.close()

    raw = path.read_bytes()
    assert b"SecretAccount" not in raw  # имя счёта не должно читаться в открытом виде


def test_wrong_password_cannot_open(tmp_path):
    path = tmp_path / "wallet.db.enc"
    db = Database(path=path, encryption=_manager("right"))
    db.connect()
    db.save()
    db.close()

    db_wrong = Database(path=path, encryption=_manager("wrong"))
    with pytest.raises(Exception):
        db_wrong.connect()
