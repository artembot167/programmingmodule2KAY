"""Відкриті приклади 05 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(5)

PUBLIC = [({'exercise': 'Присідання', 'muscle': 'Ноги', 'sets': '4', 'reps': '10', 'weight_kg': '80'},
  {'exercise': 'Присідання',
   'muscle': 'ноги',
   'sets': 4,
   'reps': 10,
   'weight_kg': 80.0,
   'tonnage': 3200.0}),
 ({'exercise': ' Жим ', 'muscle': 'груди', 'sets': '3', 'reps': '8', 'weight_kg': '60.5'},
  {'exercise': 'Жим',
   'muscle': 'груди',
   'sets': 3,
   'reps': 8,
   'weight_kg': 60.5,
   'tonnage': 1452.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
