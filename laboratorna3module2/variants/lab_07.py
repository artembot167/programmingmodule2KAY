"""Лабораторна робота 3. Задача 7: сторінка товару, вакансії чи книги.

Правила — у student.md (розділ 7, задача 7) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_07.py
"""
from bs4 import BeautifulSoup


def parse_detail(html: str, cfg: dict) -> dict:
    """Повертає {"title": ..., "specs": {ключ: значення}} за правилами задачі 7."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
