"""Відкриті приклади 15 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(15)

PUBLIC = [({'house': 'Будинок 1', 'district': 'Центр', 'kwh': '350.5', 'tariff': '4.32', 'season': 'зима'},
  {'house': 'Будинок 1',
   'district': 'центр',
   'kwh': 350.5,
   'tariff': 4.32,
   'season': 'зима',
   'cost': 1514.16}),
 ({'house': ' Будинок 2 ', 'district': 'центр', 'kwh': '120', 'tariff': '4.32', 'season': 'літо'},
  {'house': 'Будинок 2',
   'district': 'центр',
   'kwh': 120.0,
   'tariff': 4.32,
   'season': 'літо',
   'cost': 518.4})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
