"""Відкриті приклади 18 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(18)

PUBLIC = [({'time': '10:00:00', 'service': 'Auth', 'level': 'INFO', 'status': '200', 'latency_ms': '35'},
  {'time': '10:00:00',
   'service': 'auth',
   'level': 'info',
   'status': 200,
   'latency_ms': 35,
   'slow': False}),
 ({'time': ' 10:00:05 ',
   'service': 'auth',
   'level': 'error',
   'status': '500',
   'latency_ms': '1200'},
  {'time': '10:00:05',
   'service': 'auth',
   'level': 'error',
   'status': 500,
   'latency_ms': 1200,
   'slow': True})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
