"""Відкриті приклади 27 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(27)

PUBLIC = [({'ip': '192.168.0.1', 'kind': 'Роутер', 'uptime_h': '720.5', 'loss_pct': '0.5', 'mbps': '100'},
  {'ip': '192.168.0.1',
   'kind': 'роутер',
   'uptime_h': 720.5,
   'loss_pct': 0.5,
   'mbps': 100.0,
   'reliable': True}),
 ({'ip': ' 10.0.0.5 ', 'kind': 'сервер', 'uptime_h': '5000', 'loss_pct': '0', 'mbps': '1000'},
  {'ip': '10.0.0.5',
   'kind': 'сервер',
   'uptime_h': 5000.0,
   'loss_pct': 0.0,
   'mbps': 1000.0,
   'reliable': True})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
