"""Відкриті тести задачі 7: Тайм-аути й класифікація результату.

Запуск: pytest tests/test_variant_07.py
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
    """Набір 1: Класифікація: успіх і помилки клієнта."""
    assert (m.probe(api.url, "/api/v1/books/99")) == {"kind": "помилка клієнта", "status": 404, "data": {"error": "запис 99 не знайдено"}}


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Класифікація: збої сервера й мережі."""
    dead = f"http://127.0.0.1:{free_port()}"
    assert (m.probe(dead, "/api/v1/stations", timeout=1)) == {"kind": "немає з'єднання", "status": None, "data": None}


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Класифікація: некоректний тайм-аут і незвичні коди."""
    raises(ValueError, "Тайм-аут має бути додатним", lambda: m.probe(api.url, "/api/v1/routes", timeout=0))


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T07-S1-0", "T07-S2-0", "T07-S3-0"])
def test_task_07(scenario, api, spy, tmp_path):
    scenario(load(7), api, tmp_path)
    check_conventions(api, spy)
