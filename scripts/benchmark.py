"""Замер производительности слоя доступа к данным.

Воспроизводит цифры из раздела 5.7 пояснительной записки: время вставки
большого числа операций и время фильтрованных запросов. Запуск:

    python scripts/benchmark.py
"""

from __future__ import annotations

import time
from datetime import datetime
from decimal import Decimal

from wallet.core.db import Database
from wallet.models import Account, Category, CategoryKind, Transaction, TransactionType
from wallet.repositories import (AccountRepository, CategoryRepository,
                                 TransactionRepository)

N = 5000
QUERIES = 100


def main() -> None:
    db = Database()
    db.connect()
    accounts = AccountRepository(db.connection)
    categories = CategoryRepository(db.connection)
    transactions = TransactionRepository(db.connection)

    account = accounts.add(Account(name="Тест"))
    cat_ids = [
        categories.add(Category(name=f"C{i}", kind=CategoryKind.EXPENSE)).id
        for i in range(10)
    ]

    start = time.perf_counter()
    for i in range(N):
        transactions.add(Transaction(
            amount=Decimal("10"), type=TransactionType.EXPENSE,
            account_id=account.id, category_id=cat_ids[i % 10],
            created_at=datetime(2026, 1, 1)))
    insert_time = time.perf_counter() - start

    start = time.perf_counter()
    rows = []
    for _ in range(QUERIES):
        rows = transactions.list_filtered(category_id=cat_ids[5])
    query_time = time.perf_counter() - start

    print(f"Вставка {N} операций: {insert_time:.3f} с "
          f"({insert_time / N * 1000:.3f} мс/операцию)")
    print(f"{QUERIES} фильтрованных запросов: {query_time:.3f} с "
          f"({query_time / QUERIES * 1000:.3f} мс/запрос, "
          f"{len(rows)} записей в выборке)")


if __name__ == "__main__":
    main()
