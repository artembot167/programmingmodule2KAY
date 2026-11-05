"""Відкриті тести задачі 9: Сесія й токен.

Запуск: pytest tests/test_variant_09.py
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
    """Набір 1: Нотатки до книг: сесія з токеном."""
    r = m.fetch_notes(api.url, "books", [1, 2, 99], "student-token")
    assert (r["notes"], r["errors"]) == ({1: "Службова нотатка до запису «Кобзар»", 2: "Службова нотатка до запису «Лісова пісня»"}, {99: 404})


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Нотатки до метеостанцій: недійсний токен і збій."""
    raises(PermissionError, "Недійсний токен", lambda: m.fetch_notes(api.url, "stations", [4, 5, 6], "bad"))


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Нотатки до маршрутів: одне з'єднання."""
    r = m.fetch_notes(api.url, "routes", [7, 8], "student-token")
    assert (r["notes"], len({e["port"] for e in api.log})) == ({7: "Службова нотатка до запису «О-302»", 8: "Службова нотатка до запису «Х-401»"}, 1)


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T09-S1-0", "T09-S2-0", "T09-S3-0"])
def test_task_09(scenario, api, spy, tmp_path):
    scenario(load(9), api, tmp_path)
    check_conventions(api, spy)
