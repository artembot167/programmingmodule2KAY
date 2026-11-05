"""Відкриті приклади 03 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(3)

PUBLIC = [({'student': 'Іваненко І.',
   'course': 'Математика',
   'module1': '45',
   'module2': '48',
   'exam': '90'},
  {'student': 'Іваненко І.',
   'course': 'математика',
   'module1': 45,
   'module2': 48,
   'exam': 90,
   'total': 183}),
 ({'student': ' Петренко П. ',
   'course': 'математика',
   'module1': '30',
   'module2': '25',
   'exam': '60'},
  {'student': 'Петренко П.',
   'course': 'математика',
   'module1': 30,
   'module2': 25,
   'exam': 60,
   'total': 115})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
