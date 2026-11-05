"""Відкриті тести задачі 1: Безпечне завантаження сторінки.

Запуск: pytest tests/test_lab_01.py   (лише свій набір: pytest tests/test_lab_01.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T01-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 1]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_01(tag, func, env):
    func(load(1), env)
