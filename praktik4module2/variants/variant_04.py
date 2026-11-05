"""Задача 4. Умовний запит і кеш.

Правила: student.md, розділ «Опис задач», задача 4.
Відкриті тести: pytest tests/test_variant_04.py
"""

import requests  # noqa: F401


def conditional_get(base_url: str, resource: str, item_id: int, cache: dict) -> tuple:
    """Виконує умовний запит за ETag і оновлює кеш."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
