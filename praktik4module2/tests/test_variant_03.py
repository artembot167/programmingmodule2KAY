"""Відкриті тести задачі 3: Пагінація.

Запуск: pytest tests/test_variant_03.py
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
    """Набір 1: Усі книги по сторінках."""
    items = m.collect_all(api.url, "books")
    assert (len(items), items[-1]["title"], len(api.log)) == (12, "Бояриня", 3)


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Метеостанції: обмеження кількості сторінок."""
    items = m.collect_all(api.url, "stations", page_size=4, max_pages=2)
    assert ([item["id"] for item in items]) == [1, 2, 3, 4, 5, 6, 7, 8]


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Маршрути: дрібні сторінки й збій посеред читання."""
    items = m.collect_all(api.url, "routes", page_size=3)
    assert (len(items), items[-1]["number"]) == (12, "К-104")


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T03-S1-0", "T03-S2-0", "T03-S3-0"])
def test_task_03(scenario, api, spy, tmp_path):
    scenario(load(3), api, tmp_path)
    check_conventions(api, spy)
