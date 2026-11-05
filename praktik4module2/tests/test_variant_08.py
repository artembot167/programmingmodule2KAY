"""Відкриті тести задачі 8: Повторні спроби з паузою.

Запуск: pytest tests/test_variant_08.py
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
    """Набір 1: Повтор після 503: експоненційна пауза."""
    api.inject(status=503, times=2)
    pauses = []
    r = m.get_json_with_retry(api.url, "/api/v1/books/1", sleep=pauses.append)
    assert (r["attempts"], pauses) == (3, [1.0, 2.0])


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Повтор після 429: Retry-After."""
    api.inject(status=429, headers={"Retry-After": "3"})
    pauses = []
    r = m.get_json_with_retry(api.url, "/api/v1/stations/11", sleep=pauses.append)
    assert (r["pauses"], pauses) == ([3], [3])


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Повтор після збою мережі й тайм-ауту."""
    dead = f"http://127.0.0.1:{free_port()}"
    pauses = []
    raises(RuntimeError, "Не вдалося після 2 спроб: немає з'єднання", lambda: m.get_json_with_retry(dead, "/api/v1/routes", attempts=2, sleep=pauses.append))


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T08-S1-0", "T08-S2-0", "T08-S3-0"])
def test_task_08(scenario, api, spy, tmp_path):
    scenario(load(8), api, tmp_path)
    check_conventions(api, spy)
