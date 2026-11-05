"""Відкриті тести задачі 4: Умовний запит і кеш.

Запуск: pytest tests/test_variant_04.py
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
    """Набір 1: Кеш книги: перший, повторний і змінений запит."""
    cache = {}
    assert ([m.conditional_get(api.url, "books", 3, cache)[1], m.conditional_get(api.url, "books", 3, cache)[1]]) == ["мережа", "кеш"]


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Кеш метеостанції: застарілий ETag і збій."""
    cache = {11: {"etag": '"11-0"', "data": {}}}
    assert (m.conditional_get(api.url, "stations", 11, cache)[1], cache[11]["etag"]) == ("мережа", '"11-1"')


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Кеш маршрутів: два записи та запис без ETag."""
    cache = {7: {"etag": None, "data": {}}}
    assert (m.conditional_get(api.url, "routes", 7, cache)[1], "if-none-match" in api.log[0]["headers"]) == ("мережа", False)


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T04-S1-0", "T04-S2-0", "T04-S3-0"])
def test_task_04(scenario, api, spy, tmp_path):
    scenario(load(4), api, tmp_path)
    check_conventions(api, spy)
