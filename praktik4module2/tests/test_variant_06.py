"""Відкриті тести задачі 6: Створення запису: POST, JSON і токен.

Запуск: pytest tests/test_variant_06.py
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
Сервер піднімається локально (фікстура api), інтернет не потрібен.
"""
import pytest
from conftest import check_conventions, free_port, load, raises  # noqa: F401

SCENARIOS = []


def scenario(func):
    SCENARIOS.append(func)
    return func


@scenario
def example_set_1(m, api, tmp):
    """Набір 1: Додавання книги."""
    assert (m.create_item(api.url, "books", {"title": "Вечір", "author": "Іван Франко", "pages": 30}, "admin-token")) == {"id": 13, "title": "Вечір", "author": "Іван Франко", "genre": None, "pages": 30, "price": None}


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Додавання метеостанції."""
    assert (m.create_item(api.url, "stations", {"name": "Тернопіль", "city": "Тернопіль", "altitude": 320}, "admin-token")) == {"id": 13, "name": "Тернопіль", "city": "Тернопіль", "altitude": 320, "temp": None, "humidity": None, "status": None}


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Додавання маршруту і права доступу."""
    raises(PermissionError, "Недостатньо прав для запису", lambda: m.create_item(api.url, "routes", {"number": "К-105", "origin": "Київ", "destination": "Суми"}, "student-token"))


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T06-S1-0", "T06-S2-0", "T06-S3-0"])
def test_task_06(scenario, api, spy, tmp_path):
    scenario(load(6), api, tmp_path)
    check_conventions(api, spy)
