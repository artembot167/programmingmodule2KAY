"""Відкриті тести задачі 10: Повний конвеєр збору.

Запуск: pytest tests/test_lab_10.py   (лише свій набір: pytest tests/test_lab_10.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T10-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 10]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_10(tag, func, env):
    func(load(10), env)
