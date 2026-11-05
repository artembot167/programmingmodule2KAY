"""Задача 1. Один запит і статуси.

Правила: student.md, розділ «Опис задач», задача 1.
Відкриті тести: pytest tests/test_variant_01.py
"""

import requests  # noqa: F401


def get_item(base_url: str, resource: str, item_id: int) -> dict | None:
    """Виконує один запит GET за ідентифікатором і обробляє коди стану."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
