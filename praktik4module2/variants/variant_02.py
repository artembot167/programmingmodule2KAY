"""Задача 2. Параметри запиту.

Правила: student.md, розділ «Опис задач», задача 2.
Відкриті тести: pytest tests/test_variant_02.py
"""

import requests  # noqa: F401


def search_items(base_url: str, resource: str, filters: dict | None = None, sort: str | None = None, descending: bool = False, limit: int = 5) -> dict:
    """Шукає записи за фільтрами, сортуванням і розміром сторінки (параметри запиту)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
