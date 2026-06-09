"""Хранилище зашифрованной БД, защищённое паролем пользователя.

Каталог данных содержит два файла:
    wallet.salt    — соль для PBKDF2 (не является секретом, хранится открыто);
    wallet.db.enc  — зашифрованная (AES-256-GCM) база данных.

Ключ шифрования выводится из пароля и соли. Соль хранится отдельно, чтобы
её можно было прочитать до ввода пароля; сами данные без верного пароля
расшифровать невозможно (при неверном пароле проверка целостности GCM
завершается ошибкой).
"""

from __future__ import annotations

from pathlib import Path

from wallet.core.db import Database
from wallet.core.security import EncryptionManager, derive_key, generate_salt

SALT_FILE = "wallet.salt"
DB_FILE = "wallet.db.enc"


class InvalidPasswordError(Exception):
    """Введён неверный пароль — расшифровать базу данных не удалось."""


def _salt_path(data_dir: Path) -> Path:
    return data_dir / SALT_FILE


def _db_path(data_dir: Path) -> Path:
    return data_dir / DB_FILE


def vault_exists(data_dir: str | Path) -> bool:
    data_dir = Path(data_dir)
    return _salt_path(data_dir).exists() and _db_path(data_dir).exists()


def init_vault(data_dir: str | Path, password: str) -> Database:
    """Создать новое хранилище с заданным паролем."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    if vault_exists(data_dir):
        raise FileExistsError("Хранилище уже существует в данном каталоге")

    salt = generate_salt()
    _salt_path(data_dir).write_bytes(salt)
    key = derive_key(password, salt)

    db = Database(path=_db_path(data_dir), encryption=EncryptionManager(key))
    db.connect()
    db.save()
    return db


def change_password(db: Database, new_password: str) -> None:
    """Сменить пароль открытого хранилища: новая соль, ключ и перешифрование."""
    if db.path is None:
        raise ValueError("Хранилище не связано с файлом")
    if not new_password:
        raise ValueError("Пароль не может быть пустым")
    data_dir = db.path.parent
    salt = generate_salt()
    _salt_path(data_dir).write_bytes(salt)
    db.encryption = EncryptionManager(derive_key(new_password, salt))
    db.save()


def open_vault(data_dir: str | Path, password: str) -> Database:
    """Открыть существующее хранилище. При неверном пароле — ошибка."""
    data_dir = Path(data_dir)
    if not vault_exists(data_dir):
        raise FileNotFoundError("Хранилище не найдено")

    salt = _salt_path(data_dir).read_bytes()
    key = derive_key(password, salt)
    db = Database(path=_db_path(data_dir), encryption=EncryptionManager(key))
    try:
        db.connect()
    except Exception as exc:  # noqa: BLE001 - неверный ключ -> ошибка расшифровки
        db.close()
        raise InvalidPasswordError("Неверный пароль") from exc
    return db
