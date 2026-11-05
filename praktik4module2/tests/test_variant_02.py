"""Відкриті тести задачі 2: Параметри запиту.

Запуск: pytest tests/test_variant_02.py
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
    """Набір 1: Пошук книг: автор, жанр, сортування."""
    r = m.search_items(api.url, "books", {"author": "Леся Українка"})
    assert (r["count"], [item["id"] for item in r["items"]]) == (3, [2, 7, 12])


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Пошук метеостанцій: місто, статус, висота."""
    r = m.search_items(api.url, "stations", {"status": "на обслуговуванні"}, "altitude", True, 2)
    assert (r["count"], [item["id"] for item in r["items"]]) == (3, [12, 3])


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Пошук маршрутів і помилки параметрів."""
    r = m.search_items(api.url, "routes", {"q": "К-10"}, sort="fare", descending=True, limit=2)
    assert (r["count"], [item["id"] for item in r["items"]]) == (4, [12, 3])


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T02-S1-0", "T02-S2-0", "T02-S3-0"])
def test_task_02(scenario, api, spy, tmp_path):
    scenario(load(2), api, tmp_path)
    check_conventions(api, spy)
