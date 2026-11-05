"""Відкриті приклади 14 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(14)

PUBLIC = [({'currency': 'USD', 'bank': 'Банк А', 'buy': '39.5', 'sell': '40.1'},
  {'currency': 'USD', 'bank': 'банк а', 'buy': 39.5, 'sell': 40.1, 'spread': 0.6}),
 ({'currency': ' EUR ', 'bank': 'банк а', 'buy': '42', 'sell': '43.25'},
  {'currency': 'EUR', 'bank': 'банк а', 'buy': 42.0, 'sell': 43.25, 'spread': 1.25})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
