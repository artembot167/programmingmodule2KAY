"""Відкриті приклади 07 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(7)

PUBLIC = [({'flight': 'PS101',
   'route': 'Київ-Львів',
   'duration_min': '70',
   'delay_min': '0',
   'passengers': '120'},
  {'flight': 'PS101',
   'route': 'Київ-Львів',
   'duration_min': 70,
   'delay_min': 0,
   'passengers': 120,
   'late': False}),
 ({'flight': ' AB202 ',
   'route': 'Київ-Львів',
   'duration_min': '75',
   'delay_min': '20',
   'passengers': '90'},
  {'flight': 'AB202',
   'route': 'Київ-Львів',
   'duration_min': 75,
   'delay_min': 20,
   'passengers': 90,
   'late': True})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
