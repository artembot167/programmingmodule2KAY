"""Задача 9. Сесія й токен.

Правила: student.md, розділ «Опис задач», задача 9.
Відкриті тести: pytest tests/test_variant_09.py
"""

import requests  # noqa: F401


def fetch_notes(base_url: str, resource: str, ids: list, token: str) -> dict:
    """Читає захищені нотатки через одну сесію з токеном."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
