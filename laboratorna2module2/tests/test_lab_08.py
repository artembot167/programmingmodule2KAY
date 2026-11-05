"""Відкриті приклади 08 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(8)

PUBLIC = [({'visit_id': '100001',
   'department': 'Терапія',
   'duration_min': '30',
   'cost': '500',
   'status': 'завершено'},
  {'visit_id': '100001',
   'department': 'терапія',
   'duration_min': 30,
   'cost': 500.0,
   'status': 'завершено',
   'cost_per_min': 16.67}),
 ({'visit_id': ' 100002 ',
   'department': 'терапія',
   'duration_min': '45',
   'cost': '650.5',
   'status': 'Скасовано'},
  {'visit_id': '100002',
   'department': 'терапія',
   'duration_min': 45,
   'cost': 650.5,
   'status': 'скасовано',
   'cost_per_min': 14.46})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
