"""Задача 7. Регресія й діаграма розсіювання.

Правила: student.md, розділ «Опис задач», задача 7.
Відкриті тести: pytest tests/test_variant_07.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок з ендпоінтами /points і /regression."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує діаграму розсіювання з лінією регресії; payload = {"points": [...], "regression": {...}}."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Робить два запити (/points і cfg["report_url"]) через client.get і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
