"""Відкриті тести задачі 10: Пакетна обробка і файл результатів.

Запуск: pytest tests/test_variant_10.py
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
    """Набір 1: Пакет книг: файл результатів."""
    ids_file, out_file = tmp / "ids.txt", tmp / "report.json"
    ids_file.write_text("# список книг\n1\n3\n99\n3\n", encoding="utf-8")
    assert (m.run_batch(api.url, "books", ids_file, out_file)) == {"requested": 3, "found": 2, "missing": 1, "failed": 0}


@scenario
def example_set_2(m, api, tmp):
    """Набір 2: Пакет метеостанцій: збій посеред пакета."""
    api.inject(status=503, after=1, match="/api/v1/stations")
    ids_file, out_file = tmp / "ids.txt", tmp / "report.json"
    ids_file.write_text("11\n12\n7\n", encoding="utf-8")
    assert (m.run_batch(api.url, "stations", ids_file, out_file)) == {"requested": 3, "found": 2, "missing": 0, "failed": 1}


@scenario
def example_set_3(m, api, tmp):
    """Набір 3: Пакет маршрутів: помилки у вхідному файлі."""
    ids_file, out_file = tmp / "ids.txt", tmp / "report.json"
    ids_file.write_text("7\nabc\n8\n", encoding="utf-8")
    raises(ValueError, "Рядок 2: не є цілим числом", lambda: m.run_batch(api.url, "routes", ids_file, out_file))


@pytest.mark.parametrize("scenario", SCENARIOS, ids=["T10-S1-0", "T10-S2-0", "T10-S3-0"])
def test_task_10(scenario, api, spy, tmp_path):
    scenario(load(10), api, tmp_path)
    check_conventions(api, spy)
