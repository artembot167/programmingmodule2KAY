"""Задача 1. Список ресурсу з фільтрами.

Правила: student.md, розділ «Опис задач», задача 1.
Відкриті тести: pytest tests/test_variant_01.py
"""
from fastapi import FastAPI


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    """Створює застосунок FastAPI зі списком ресурсу (фільтри group, min_value, limit) і записом за номером."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def build_figure(payload: dict, cfg: dict):
    """Будує горизонтальну діаграму значень за відповіддю списку; повертає Figure."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі


def chart_from_service(client, cfg: dict):
    """Отримує відповідь за cfg["report_url"] через client.get і повертає графік."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
