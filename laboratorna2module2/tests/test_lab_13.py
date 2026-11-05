"""Відкриті приклади 13 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(13)

PUBLIC = [({'brand': 'Skoda', 'klass': 'Економ', 'days': '3', 'price_per_day': '800', 'insurance': 'ні'},
  {'brand': 'Skoda',
   'klass': 'економ',
   'days': 3,
   'price_per_day': 800.0,
   'insurance': False,
   'total': 2400.0}),
 ({'brand': ' BMW ', 'klass': 'бізнес', 'days': '2', 'price_per_day': '2500', 'insurance': 'так'},
  {'brand': 'BMW',
   'klass': 'бізнес',
   'days': 2,
   'price_per_day': 2500.0,
   'insurance': True,
   'total': 5500.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
