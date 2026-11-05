"""Відкриті приклади 16 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(16)

PUBLIC = [({'nick': 'Alpha', 'mode': 'соло', 'wins': '30', 'losses': '10', 'minutes': '600'},
  {'nick': 'Alpha',
   'mode': 'соло',
   'wins': 30,
   'losses': 10,
   'minutes': 600,
   'win_rate_pct': 75.0}),
 ({'nick': ' Beta ', 'mode': 'Команда', 'wins': '5', 'losses': '15', 'minutes': '240'},
  {'nick': 'Beta',
   'mode': 'команда',
   'wins': 5,
   'losses': 15,
   'minutes': 240,
   'win_rate_pct': 25.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
