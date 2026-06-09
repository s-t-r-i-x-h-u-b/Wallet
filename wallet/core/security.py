"""Модуль безопасности: вывод ключа из пароля и шифрование данных.

Ключ шифрования не хранится в открытом виде, а выводится из пароля
пользователя функцией PBKDF2-HMAC-SHA256 с использованием соли.
Шифрование данных выполняется алгоритмом AES-256 в режиме GCM, что
обеспечивает конфиденциальность и контроль целостности.

В прототипе шифруется весь файл базы данных «в покое». В производственной
версии аналогичную задачу решает расширение SQLCipher (прозрачное
постраничное шифрование); используемый алгоритм (AES-256) и схема вывода
ключа (PBKDF2) при этом совпадают.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os

from Crypto.Cipher import AES

PBKDF2_ITERATIONS = 200_000
KEY_LENGTH = 32  # 256 бит -> AES-256
SALT_LENGTH = 16
NONCE_LENGTH = 12
TAG_LENGTH = 16


def generate_salt() -> bytes:
    """Сгенерировать криптографически случайную соль."""
    return os.urandom(SALT_LENGTH)


def derive_key(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """Вывести 256-битный ключ из пароля и соли (PBKDF2-HMAC-SHA256)."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=KEY_LENGTH
    )


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    """Вернуть (хеш пароля, соль) в base64 для хранения в БД."""
    if salt is None:
        salt = generate_salt()
    key = derive_key(password, salt)
    return base64.b64encode(key).decode(), base64.b64encode(salt).decode()


def verify_password(password: str, password_hash_b64: str, salt_b64: str) -> bool:
    """Проверить пароль по сохранённым хешу и соли (защита от тайминг-атак)."""
    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(password_hash_b64)
    actual = derive_key(password, salt)
    return hmac.compare_digest(expected, actual)


class EncryptionManager:
    """Шифрование/расшифрование произвольных данных ключом AES-256-GCM."""

    def __init__(self, key: bytes):
        if len(key) != KEY_LENGTH:
            raise ValueError(f"Ключ должен быть длиной {KEY_LENGTH} байт")
        self._key = key

    @classmethod
    def from_password(cls, password: str, salt: bytes) -> "EncryptionManager":
        """Создать менеджер, выведя ключ из пароля пользователя."""
        return cls(derive_key(password, salt))

    def encrypt(self, data: bytes) -> bytes:
        """Зашифровать данные. Результат: nonce(12) + tag(16) + шифртекст."""
        nonce = os.urandom(NONCE_LENGTH)
        cipher = AES.new(self._key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return nonce + tag + ciphertext

    def decrypt(self, token: bytes) -> bytes:
        """Расшифровать данные. При неверном ключе будет исключение (ValueError)."""
        nonce = token[:NONCE_LENGTH]
        tag = token[NONCE_LENGTH:NONCE_LENGTH + TAG_LENGTH]
        ciphertext = token[NONCE_LENGTH + TAG_LENGTH:]
        cipher = AES.new(self._key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)
