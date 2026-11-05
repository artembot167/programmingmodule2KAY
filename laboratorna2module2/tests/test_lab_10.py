"""Відкриті приклади 10 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(10)

PUBLIC = [({'dish': 'Борщ', 'category': 'Супи', 'portions': '2', 'price': '85', 'discount_pct': '10'},
  {'dish': 'Борщ',
   'category': 'супи',
   'portions': 2,
   'price': 85.0,
   'discount_pct': 10,
   'amount': 153.0}),
 ({'dish': ' Вареники ',
   'category': 'основні',
   'portions': '3',
   'price': '120.5',
   'discount_pct': '0'},
  {'dish': 'Вареники',
   'category': 'основні',
   'portions': 3,
   'price': 120.5,
   'discount_pct': 0,
   'amount': 361.5})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
