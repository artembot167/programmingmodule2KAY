"""Відкриті приклади 19 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(19)

PUBLIC = [({'abonent': '0671234567',
   'call_type': 'Вихідний',
   'seconds': '125',
   'tariff_min': '1.5',
   'region': 'Київ'},
  {'abonent': '0671234567',
   'call_type': 'вихідний',
   'seconds': 125,
   'tariff_min': 1.5,
   'region': 'київ',
   'minutes': 3,
   'cost': 4.5}),
 ({'abonent': ' 0501112233 ',
   'call_type': 'вхідний',
   'seconds': '60',
   'tariff_min': '0',
   'region': 'київ'},
  {'abonent': '0501112233',
   'call_type': 'вхідний',
   'seconds': 60,
   'tariff_min': 0.0,
   'region': 'київ',
   'minutes': 1,
   'cost': 0.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
