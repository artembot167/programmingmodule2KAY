"""Відкриті приклади 22 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(22)

PUBLIC = [({'station': 'St1', 'parameter': 'PM2.5', 'value': '12.5', 'unit': 'мкг/м3', 'quality': 'ok'},
  {'station': 'St1',
   'parameter': 'pm2.5',
   'value': 12.5,
   'unit': 'мкг/м3',
   'quality': 'ok',
   'high': False}),
 ({'station': ' St2 ', 'parameter': 'pm10', 'value': '30', 'unit': 'мкг/м3', 'quality': 'сумнівно'},
  {'station': 'St2',
   'parameter': 'pm10',
   'value': 30.0,
   'unit': 'мкг/м3',
   'quality': 'сумнівно',
   'high': True})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
