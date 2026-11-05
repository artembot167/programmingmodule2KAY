"""Задача 6. Створення запису: POST, JSON і токен.

Правила: student.md, розділ «Опис задач», задача 6.
Відкриті тести: pytest tests/test_variant_06.py
"""

import requests  # noqa: F401


def create_item(base_url: str, resource: str, payload: dict, token: str) -> dict:
    """Створює запис запитом POST з JSON і токеном."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
