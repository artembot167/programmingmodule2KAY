"""Відкриті приклади 20 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(20)

PUBLIC = [({'ticker': 'ABC', 'day': '1', 'open': '100', 'close': '105', 'volume': '5000'},
  {'ticker': 'ABC', 'day': 1, 'open': 100.0, 'close': 105.0, 'volume': 5000, 'change_pct': 5.0}),
 ({'ticker': ' ABC ', 'day': '2', 'open': '105', 'close': '99.75', 'volume': '4200'},
  {'ticker': 'ABC', 'day': 2, 'open': 105.0, 'close': 99.75, 'volume': 4200, 'change_pct': -5.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
