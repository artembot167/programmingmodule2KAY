"""Задача 10. Пакетна обробка і файл результатів.

Правила: student.md, розділ «Опис задач», задача 10.
Відкриті тести: pytest tests/test_variant_10.py
"""

import requests  # noqa: F401


def run_batch(base_url: str, resource: str, ids_path, out_path) -> dict:
    """Читає список ідентифікаторів із файла, опитує API й зберігає файл результатів."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
