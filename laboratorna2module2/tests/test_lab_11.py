"""Відкриті приклади 11 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(11)

PUBLIC = [({'sensor_id': 'TS', 'room': 'Кухня', 'temp_c': '22.5', 'humidity': '45', 'ok': 'так'},
  {'sensor_id': 'TS',
   'room': 'кухня',
   'temp_c': 22.5,
   'humidity': 45,
   'ok': True,
   'anomaly': False}),
 ({'sensor_id': ' HM ', 'room': 'кухня', 'temp_c': '-5', 'humidity': '80', 'ok': 'так'},
  {'sensor_id': 'HM',
   'room': 'кухня',
   'temp_c': -5.0,
   'humidity': 80,
   'ok': True,
   'anomaly': True})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
