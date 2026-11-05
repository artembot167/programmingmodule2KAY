"""Відкриті приклади 01 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(1)

PUBLIC = [({'isbn': '9780000000001',
   'title': 'Кобзар',
   'author': 'Шевченко',
   'pages': '320',
   'price': '150.5',
   'available': 'так'},
  {'isbn': '9780000000001',
   'title': 'Кобзар',
   'author': 'Шевченко',
   'pages': 320,
   'price': 150.5,
   'available': True,
   'pages_per_uah': 2.13}),
 ({'isbn': ' 9780000000002 ',
   'title': 'Тіні забутих предків',
   'author': 'Коцюбинський',
   'pages': '180',
   'price': '99',
   'available': 'ні'},
  {'isbn': '9780000000002',
   'title': 'Тіні забутих предків',
   'author': 'Коцюбинський',
   'pages': 180,
   'price': 99.0,
   'available': False,
   'pages_per_uah': 1.82})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
