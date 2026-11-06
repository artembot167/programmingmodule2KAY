"""Задача 8. Кілька серій і легенда.

Правила: student.md, розділ «Опис задач», задача 8.
Відкриті тести: pytest tests/test_variant_08.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок з ендпоінтом /lines (повторюваний параметр names)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує лінійну діаграму з кількох серій, різним оформленням ліній і легендою; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Отримує серії за cfg["report_url"] через client.get і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
