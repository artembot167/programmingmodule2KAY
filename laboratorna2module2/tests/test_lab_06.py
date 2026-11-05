"""Відкриті приклади 06 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(6)

PUBLIC = [({'room': '101', 'kind': 'Стандарт', 'nights': '3', 'price_per_night': '1200', 'breakfast': 'так'},
  {'room': '101',
   'kind': 'стандарт',
   'nights': 3,
   'price_per_night': 1200.0,
   'breakfast': True,
   'total': 4050.0}),
 ({'room': ' 202 ', 'kind': 'люкс', 'nights': '2', 'price_per_night': '3500.5', 'breakfast': 'ні'},
  {'room': '202',
   'kind': 'люкс',
   'nights': 2,
   'price_per_night': 3500.5,
   'breakfast': False,
   'total': 7001.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
