"""Задача 2. Підсумки за групами.

Правила: student.md, розділ «Опис задач», задача 2.
Відкриті тести: pytest tests/test_variant_02.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок з ендпоінтами /groups і /summary (параметр stat)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує стовпчикову діаграму підсумків із підписами значень; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Отримує відповідь за cfg["report_url"] через client.get і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
