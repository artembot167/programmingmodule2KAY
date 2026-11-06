"""Задача 5. Рейтинг найкращих записів.

Правила: student.md, розділ «Опис задач», задача 5.
Відкриті тести: pytest tests/test_variant_05.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок з ендпоінтом /top (параметри n, order, group)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує горизонтальну діаграму рейтингу з виділеним лідером; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Отримує рейтинг за cfg["report_url"] через client.get і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
