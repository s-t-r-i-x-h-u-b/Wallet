"""Сервис аутентификации и регистрации пользователя."""

from __future__ import annotations

from typing import Optional

from wallet.core import security
from wallet.models import User
from wallet.repositories import UserRepository


class AuthService:
    """Регистрация и вход по паролю.

    Пароль не хранится в открытом виде — сохраняются его хеш (PBKDF2) и соль.
    """

    def __init__(self, users: UserRepository):
        self.users = users

    def register(self, name: str, password: str) -> User:
        if not name or not password:
            raise ValueError("Имя и пароль не могут быть пустыми")
        if self.users.get_by_name(name) is not None:
            raise ValueError("Пользователь с таким именем уже существует")
        password_hash, salt = security.hash_password(password)
        user = User(name=name, password_hash=password_hash, salt=salt)
        return self.users.add(user)

    def login(self, name: str, password: str) -> Optional[User]:
        """Вернуть пользователя при верном пароле, иначе None."""
        user = self.users.get_by_name(name)
        if user is None:
            return None
        if security.verify_password(password, user.password_hash, user.salt):
            return user
        return None
