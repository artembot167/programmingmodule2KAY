"""Відкриті тести задачі 1: Один запит і статуси.

Запуск: pytest tests/test_variant_01.py
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
    """Набір 1: Один запит: книга за номером."""
    assert (m.get_item(api.url, "books", 3)) == {"id": 3, "title": "Захар Беркут", "author": "Іван Франко", "genre": "повість", "pages": 210, "price": 210, "reviews": [{"user": "ігор", "rating": 4}, {"user": "марта", "rating": 3}, {"user": "софія", "rating": 4}, {"user": "тарас", "rating": None}]}


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Один запит: метеостанція за номером."""
    assert (m.get_item(api.url, "stations", 11)) == {"id": 11, "name": "Говерла", "city": "Ворохта", "altitude": 1450, "temp": -2.4, "humidity": 90, "status": "активна", "readings": [{"hour": 0, "temp": -3.0}, {"hour": 6, "temp": -2.5}, {"hour": 12, "temp": -2.0}, {"hour": 18, "temp": -2.5}]}


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Один запит: маршрут і помилки."""
    assert (m.get_item(api.url, "routes", 99)) == None


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T01-S1-0", "T01-S2-0", "T01-S3-0"])
def test_task_01(scenario, api, spy, tmp_path):
    scenario(load(1), api, tmp_path)
    check_conventions(api, spy)
