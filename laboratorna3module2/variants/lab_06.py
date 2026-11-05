"""Лабораторна робота 3. Задача 6: обхід пагінації.

Правила — у student.md (розділ 7, задача 6) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_06.py
"""
import time


def crawl_listing(fetch, start_url, parse, next_url, delay=1.0, sleep=time.sleep, max_pages=50) -> dict:
    """Обходить сторінки каталогу від start_url і повертає словник за правилами задачі 6."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
