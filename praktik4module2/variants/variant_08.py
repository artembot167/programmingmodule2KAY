"""Задача 8. Повторні спроби з паузою.

Правила: student.md, розділ «Опис задач», задача 8.
Відкриті тести: pytest tests/test_variant_08.py
"""
import time

import requests  # noqa: F401


def get_json_with_retry(base_url: str, path: str, attempts: int = 4, delay: float = 1.0, sleep=time.sleep, timeout: float = 2) -> dict:
    """Виконує запит із повторними спробами та експоненційною паузою."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
