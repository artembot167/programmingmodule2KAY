"""Задача 9. Сторінки й накопичувальний графік.

Правила: student.md, розділ «Опис задач», задача 9.
Відкриті тести: pytest tests/test_variant_09.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок зі списком, поділеним на сторінки (параметри page, size)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(items: list[dict], cfg: dict):
    """Будує накопичувальну лінію із заливкою за повним списком записів; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Збирає всі сторінки через client.get (без зайвих запитів) і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
