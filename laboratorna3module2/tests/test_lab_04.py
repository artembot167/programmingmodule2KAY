"""Відкриті тести задачі 4: Очищення ціни.

Запуск: pytest tests/test_lab_04.py   (лише свій набір: pytest tests/test_lab_04.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T04-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 4]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_04(tag, func, env):
    func(load(4), env)
