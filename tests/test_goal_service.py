"""Тесты сервиса финансовых целей."""

from __future__ import annotations

from decimal import Decimal

import pytest


def test_create_and_progress(context):
    goal = context.goal_service.create("Отпуск", Decimal("1000"))
    assert goal.progress == 0.0
    assert goal.is_reached is False


def test_contribute_updates_progress(context):
    goal = context.goal_service.create("Ноутбук", Decimal("1000"))
    updated = context.goal_service.contribute(goal.id, Decimal("250"))
    assert updated.current_amount == Decimal("250")
    assert updated.progress == 0.25


def test_goal_reached(context):
    goal = context.goal_service.create("Резерв", Decimal("500"))
    context.goal_service.contribute(goal.id, Decimal("500"))
    reached = context.goals.get(goal.id)
    assert reached.is_reached is True
    assert reached.progress == 1.0


def test_invalid_target_rejected(context):
    with pytest.raises(ValueError):
        context.goal_service.create("Плохая цель", Decimal("0"))


def test_update_goal(context):
    goal = context.goal_service.create("Старое", Decimal("1000"))
    context.goal_service.update(goal.id, title="Новое", target_amount=Decimal("2000"))
    updated = context.goals.get(goal.id)
    assert updated.title == "Новое"
    assert updated.target_amount == Decimal("2000")


def test_delete_goal(context):
    goal = context.goal_service.create("Удалить", Decimal("1000"))
    context.goal_service.delete(goal.id)
    assert context.goals.get(goal.id) is None
