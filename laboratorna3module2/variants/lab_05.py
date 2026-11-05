"""Лабораторна робота 3. Задача 5: перехід на наступну сторінку.

Правила — у student.md (розділ 7, задача 5) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_05.py
"""
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def next_page_url(html: str, current_url: str, cfg: dict):
    """Повертає абсолютну адресу наступної сторінки або None."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
