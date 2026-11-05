"""Відкриті приклади 12 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(12)

PUBLIC = [({'track': '1234567890', 'city': 'Київ', 'weight_kg': '2.5', 'cost': '90', 'status': 'доставлено'},
  {'track': '1234567890',
   'city': 'київ',
   'weight_kg': 2.5,
   'cost': 90.0,
   'status': 'доставлено',
   'cost_per_kg': 36.0}),
 ({'track': ' 2234567890 ',
   'city': 'київ',
   'weight_kg': '10',
   'cost': '150.75',
   'status': 'У дорозі'},
  {'track': '2234567890',
   'city': 'київ',
   'weight_kg': 10.0,
   'cost': 150.75,
   'status': 'у дорозі',
   'cost_per_kg': 15.07})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
