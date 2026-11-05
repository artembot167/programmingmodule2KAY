"""Відкриті тести задачі 5: Розбір вкладеного JSON.

Запуск: pytest tests/test_variant_05.py
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
    """Набір 1: Відгуки на книгу: оцінки й пропуски."""
    assert (m.nested_stats(api.url, "books", 3, "reviews", "rating")) == {"count": 3, "min": 3, "max": 4, "mean": 3.67, "skipped": 1}


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Покази метеостанції: температура за добу."""
    assert (m.nested_stats(api.url, "stations", 4, "readings", "temp")) == {"count": 4, "min": 5.8, "max": 7.0, "mean": 6.4, "skipped": 1}


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Зупинки маршруту: час у дорозі й помилки."""
    assert (m.nested_stats(api.url, "routes", 2, "stops", "minutes")) == {"count": 3, "min": 50, "max": 150, "mean": 103.33, "skipped": 0}


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T05-S1-0", "T05-S2-0", "T05-S3-0"])
def test_task_05(scenario, api, spy, tmp_path):
    scenario(load(5), api, tmp_path)
    check_conventions(api, spy)
