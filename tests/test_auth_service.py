"""Тесты сервиса аутентификации."""

from __future__ import annotations

import pytest


def test_register_and_login(context):
    context.auth.register("alex", "secret123")
    user = context.auth.login("alex", "secret123")
    assert user is not None
    assert user.name == "alex"


def test_login_with_wrong_password(context):
    context.auth.register("alex", "secret123")
    assert context.auth.login("alex", "bad") is None


def test_password_is_not_stored_plaintext(context):
    user = context.auth.register("alex", "secret123")
    assert user.password_hash != "secret123"
    assert "secret123" not in user.password_hash


def test_duplicate_registration_rejected(context):
    context.auth.register("alex", "secret123")
    with pytest.raises(ValueError):
        context.auth.register("alex", "another")
