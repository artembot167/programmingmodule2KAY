"""Відкриті приклади 28 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(28)

PUBLIC = [({'order': '500001',
   'category': 'Одяг',
   'amount': '1200',
   'reason': 'не підійшло',
   'returned': 'так'},
  {'order': '500001',
   'category': 'одяг',
   'amount': 1200.0,
   'reason': 'не підійшло',
   'returned': True,
   'refund': 1200.0}),
 ({'order': ' 500002 ', 'category': 'одяг', 'amount': '450.5', 'reason': 'брак', 'returned': 'ні'},
  {'order': '500002',
   'category': 'одяг',
   'amount': 450.5,
   'reason': 'брак',
   'returned': False,
   'refund': 0.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
