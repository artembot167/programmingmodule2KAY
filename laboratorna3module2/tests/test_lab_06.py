"""Відкриті тести задачі 6: Обхід пагінації.

Запуск: pytest tests/test_lab_06.py   (лише свій набір: pytest tests/test_lab_06.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T06-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 6]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_06(tag, func, env):
    func(load(6), env)
