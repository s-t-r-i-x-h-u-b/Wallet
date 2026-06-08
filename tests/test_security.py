"""Тесты модуля безопасности: вывод ключа, пароли, шифрование."""

from __future__ import annotations

import pytest

from wallet.core.security import (
    KEY_LENGTH,
    EncryptionManager,
    derive_key,
    generate_salt,
    hash_password,
    verify_password,
)


def test_derive_key_is_deterministic():
    salt = generate_salt()
    assert derive_key("secret", salt) == derive_key("secret", salt)


def test_derive_key_length_is_256_bit():
    assert len(derive_key("secret", generate_salt())) == KEY_LENGTH


def test_different_salt_gives_different_key():
    assert derive_key("secret", generate_salt()) != derive_key("secret", generate_salt())


def test_password_verification():
    pw_hash, salt = hash_password("p@ssw0rd")
    assert verify_password("p@ssw0rd", pw_hash, salt) is True
    assert verify_password("wrong", pw_hash, salt) is False


def test_encryption_round_trip():
    manager = EncryptionManager(derive_key("key", generate_salt()))
    data = b"confidential financial data"
    assert manager.decrypt(manager.encrypt(data)) == data


def test_decrypt_with_wrong_key_fails():
    data = b"secret"
    token = EncryptionManager(derive_key("right", b"0" * 16)).encrypt(data)
    wrong = EncryptionManager(derive_key("wrong", b"0" * 16))
    with pytest.raises(Exception):
        wrong.decrypt(token)


def test_invalid_key_length_rejected():
    with pytest.raises(ValueError):
        EncryptionManager(b"too-short")
