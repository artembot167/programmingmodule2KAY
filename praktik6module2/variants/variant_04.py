"""Задача 4. Часовий ряд за місяцями.

Правила: student.md, розділ «Опис задач», задача 4.
Відкриті тести: pytest tests/test_variant_04.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок з ендпоінтами /series (діапазон дат, суми за місяцями) і /latest."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує лінійну діаграму з позначкою максимуму; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Отримує ряд за cfg["report_url"] через client.get і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
