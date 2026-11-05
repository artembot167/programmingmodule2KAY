"""Відкриті приклади 21 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(21)

PUBLIC = [({'field': 'Поле 1',
   'crop': 'Пшениця',
   'area_ha': '50',
   'harvest_t': '225',
   'moisture_pct': '14.5'},
  {'field': 'Поле 1',
   'crop': 'пшениця',
   'area_ha': 50.0,
   'harvest_t': 225.0,
   'moisture_pct': 14.5,
   'yield_t_ha': 4.5}),
 ({'field': ' Поле 2 ',
   'crop': 'пшениця',
   'area_ha': '20.5',
   'harvest_t': '102.5',
   'moisture_pct': '13'},
  {'field': 'Поле 2',
   'crop': 'пшениця',
   'area_ha': 20.5,
   'harvest_t': 102.5,
   'moisture_pct': 13.0,
   'yield_t_ha': 5.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
