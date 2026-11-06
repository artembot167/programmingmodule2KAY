"""Відкриті тести задачі 3: Створення записів і валідація.

Запуск: pytest tests/test_variant_03.py
Тут лише приклади з карток варіантів; повний набір перевірок є у викладача.
Ідентифікатор тесту: T03-<набір>-<номер>.
"""
import pytest
from conftest import run_case

CASES = [{'kind': 'api',
  'set': 'S1',
  'steps': [['POST',
             '/holdings',
             {'name': 'Лісова пісня', 'group': 'книга', 'value': 150},
             201,
             {'id': 5, 'name': 'Лісова пісня', 'group': 'книга', 'value': 150.0}],
            ['GET', '/holdings/stats', None, 200, {'total': 5, 'by_group': {'книга': 3, 'журнал': 1, 'стаття': 1}}]]},
 {'kind': 'fig',
  'set': 'S1',
  'payload': {'total': 4, 'by_group': {'книга': 2, 'журнал': 1, 'стаття': 1}},
  'expect': {'axes': [{'title': 'Склад бібліотечного фонду',
                       'wedges': [0.5, 0.25, 0.25],
                       'texts': ['книга', 'журнал', 'стаття', '50%', '25%', '25%']}]}},
 {'kind': 'pipe',
  'set': 'S1',
  'expect': {'axes': [{'title': 'Склад бібліотечного фонду',
                       'wedges': [0.5, 0.25, 0.25],
                       'texts': ['книга', 'журнал', 'стаття', '50%', '25%', '25%']}]}},
 {'kind': 'api',
  'set': 'S2',
  'steps': [['GET',
             '/equipment/stats',
             None,
             200,
             {'total': 5, 'by_group': {"комп'ютер": 3, 'принтер': 1, 'проєктор': 1}}]]},
 {'kind': 'fig',
  'set': 'S2',
  'payload': {'total': 5, 'by_group': {"комп'ютер": 3, 'принтер': 1, 'проєктор': 1}},
  'expect': {'axes': [{'title': 'Інвентар кабінету',
                       'wedges': [0.6, 0.2, 0.2],
                       'texts': ["комп'ютер", 'принтер', 'проєктор', '60%', '20%', '20%']}]}},
 {'kind': 'pipe',
  'set': 'S2',
  'expect': {'axes': [{'title': 'Інвентар кабінету',
                       'wedges': [0.6, 0.2, 0.2],
                       'texts': ["комп'ютер", 'принтер', 'проєктор', '60%', '20%', '20%']}]}},
 {'kind': 'api',
  'set': 'S3',
  'steps': [['GET',
             '/members/stats',
             None,
             200,
             {'total': 3, 'by_group': {'шаховий': 2, 'музичний': 1, 'технічний': 0, 'спортивний': 0}}]]},
 {'kind': 'fig',
  'set': 'S3',
  'payload': {'total': 3, 'by_group': {'шаховий': 2, 'музичний': 1, 'технічний': 0, 'спортивний': 0}},
  'expect': {'axes': [{'title': 'Склад гуртків',
                       'wedges': [0.6667, 0.3333],
                       'texts': ['шаховий', 'музичний', '67%', '33%']}]}},
 {'kind': 'pipe',
  'set': 'S3',
  'expect': {'axes': [{'title': 'Склад гуртків',
                       'wedges': [0.6667, 0.3333],
                       'texts': ['шаховий', 'музичний', '67%', '33%']}]}}]


@pytest.mark.parametrize("case", CASES, ids=[f"T03-{c['set']}-{i}" for i, c in enumerate(CASES)])
def test_task_03(case):
    run_case(3, case)
