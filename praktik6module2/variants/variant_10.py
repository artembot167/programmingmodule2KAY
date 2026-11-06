"""Задача 10. Панель з двох діаграм і обробка помилок.

Правила: student.md, розділ «Опис задач», задача 10.
Відкриті тести: pytest tests/test_variant_10.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок з ендпоінтом /dashboard (параметр min_value)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує малюнок з двома діаграмами за відповіддю /dashboard; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Отримує панель за cfg["report_url"]; на 404 повертає порожній малюнок, на інші помилки кидає RuntimeError."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
