"""Задача 5. Розбір вкладеного JSON.

Правила: student.md, розділ «Опис задач», задача 5.
Відкриті тести: pytest tests/test_variant_05.py
"""

import requests  # noqa: F401


def nested_stats(base_url: str, resource: str, item_id: int, list_field: str, value_field: str) -> dict:
    """Розбирає вкладений список з JSON запису й рахує підсумок."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
