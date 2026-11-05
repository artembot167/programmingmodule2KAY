"""Лабораторна робота 3. Задача 1: безпечне завантаження сторінки.

Правила — у student.md (розділ 7, задача 1) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_01.py
"""
import requests


def fetch_html(url: str, user_agent: str = "StudyBot/1.0 (educational scraper)", timeout: float = 5) -> str:
    """Завантажує сторінку і повертає її текст або кидає ValueError за правилами задачі 1."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
