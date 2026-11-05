"""Відкриті тести задачі 9: Збереження датасету у CSV і JSON.

Запуск: pytest tests/test_lab_09.py   (лише свій набір: pytest tests/test_lab_09.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T09-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 9]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_09(tag, func, env):
    func(load(9), env)
