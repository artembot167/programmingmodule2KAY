"""Відкриті тести задачі 7: Сторінка товару, вакансії чи книги.

Запуск: pytest tests/test_lab_07.py   (лише свій набір: pytest tests/test_lab_07.py -k S2)
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
"""
import pytest
from conftest import load

from checks import CASES

PARAMS = [pytest.param(tag, func, id=f"T07-{tag}-{name}")
          for num, tag, name, func, _ in CASES if num == 7]


@pytest.mark.parametrize("tag,func", PARAMS)
def test_task_07(tag, func, env):
    func(load(7), env)
