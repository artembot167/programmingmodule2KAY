"""Відкриті тести задачі 3: Розбір сторінки каталогу.

Запуск: pytest tests/test_lab_03.py   (лише свій набір: pytest tests/test_lab_03.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T03-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 3]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_03(tag, func, env):
    func(load(3), env)
