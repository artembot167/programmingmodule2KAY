"""Відкриті приклади 09 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(9)

PUBLIC = [({'movie': 'Фільм А', 'hall': 'Зал 1', 'ticket_price': '150', 'sold': '80', 'capacity': '100'},
  {'movie': 'Фільм А',
   'hall': 'зал 1',
   'ticket_price': 150.0,
   'sold': 80,
   'capacity': 100,
   'revenue': 12000.0,
   'occupancy_pct': 80.0}),
 ({'movie': ' Фільм Б ', 'hall': 'зал 2', 'ticket_price': '120.5', 'sold': '50', 'capacity': '50'},
  {'movie': 'Фільм Б',
   'hall': 'зал 2',
   'ticket_price': 120.5,
   'sold': 50,
   'capacity': 50,
   'revenue': 6025.0,
   'occupancy_pct': 100.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
