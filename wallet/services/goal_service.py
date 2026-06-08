"""Сервис управления финансовыми целями."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from wallet.models import Goal
from wallet.repositories import GoalRepository


class GoalService:
    """Постановка целей и отслеживание прогресса их достижения."""

    def __init__(self, goals: GoalRepository):
        self.goals = goals

    def create(
        self,
        title: str,
        target_amount: Decimal,
        deadline: Optional[date] = None,
    ) -> Goal:
        if target_amount <= 0:
            raise ValueError("Целевая сумма должна быть положительной")
        return self.goals.add(
            Goal(title=title, target_amount=target_amount, deadline=deadline)
        )

    def contribute(self, goal_id: int, amount: Decimal) -> Goal:
        """Пополнить накопления по цели."""
        goal = self.goals.get(goal_id)
        if goal is None:
            raise ValueError("Цель не найдена")
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        goal.current_amount += amount
        self.goals.update(goal)
        return goal

    def list(self) -> list[Goal]:
        return self.goals.list()
