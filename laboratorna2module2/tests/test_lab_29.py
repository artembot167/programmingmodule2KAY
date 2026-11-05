"""Відкриті приклади 29 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(29)

PUBLIC = [({'campaign': 'Збір 1',
   'organization': 'Фонд А',
   'raised': '50000',
   'goal': '100000',
   'donations': '120'},
  {'campaign': 'Збір 1',
   'organization': 'фонд а',
   'raised': 50000.0,
   'goal': 100000.0,
   'donations': 120,
   'progress_pct': 50.0,
   'avg_donation': 416.67}),
 ({'campaign': ' Збір 2 ',
   'organization': 'фонд а',
   'raised': '15000.5',
   'goal': '15000',
   'donations': '45'},
  {'campaign': 'Збір 2',
   'organization': 'фонд а',
   'raised': 15000.5,
   'goal': 15000.0,
   'donations': 45,
   'progress_pct': 100.0,
   'avg_donation': 333.34})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
