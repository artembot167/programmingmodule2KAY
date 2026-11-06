"""Задача 6. Гістограма розподілу значень.

Правила: student.md, розділ «Опис задач», задача 6.
Відкриті тести: pytest tests/test_variant_06.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок з ендпоінтом /histogram (параметри bins, group)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує гістограму за готовими кошиками; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Отримує кошики за cfg["report_url"] через client.get і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
