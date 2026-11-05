"""Відкриті приклади 30 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(30)

PUBLIC = [({'route': '12', 'kind': 'Автобус', 'passengers': '4200', 'trips': '30', 'fare': '8'},
  {'route': '12',
   'kind': 'автобус',
   'passengers': 4200,
   'trips': 30,
   'fare': 8.0,
   'revenue': 33600.0,
   'per_trip': 140.0}),
 ({'route': ' 5 ', 'kind': 'трамвай', 'passengers': '3100', 'trips': '25', 'fare': '6.5'},
  {'route': '5',
   'kind': 'трамвай',
   'passengers': 3100,
   'trips': 25,
   'fare': 6.5,
   'revenue': 20150.0,
   'per_trip': 124.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
