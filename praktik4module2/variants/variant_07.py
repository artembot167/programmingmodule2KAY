"""Задача 7. Тайм-аути й класифікація результату.

Правила: student.md, розділ «Опис задач», задача 7.
Відкриті тести: pytest tests/test_variant_07.py
"""

import requests  # noqa: F401


def probe(base_url: str, path: str, timeout: float = 1.0) -> dict:
    """Виконує запит і описує його результат одним словником."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
