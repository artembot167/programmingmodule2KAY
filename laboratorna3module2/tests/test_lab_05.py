"""Відкриті тести задачі 5: Перехід на наступну сторінку.

Запуск: pytest tests/test_lab_05.py   (лише свій набір: pytest tests/test_lab_05.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T05-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 5]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_05(tag, func, env):
    func(load(5), env)
