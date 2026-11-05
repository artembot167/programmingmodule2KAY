"""Відкриті тести задачі 8: Злиття списку й сторінок деталей.

Запуск: pytest tests/test_lab_08.py   (лише свій набір: pytest tests/test_lab_08.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T08-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 8]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_08(tag, func, env):
    func(load(8), env)
