"""Відкриті приклади 23 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(23)

PUBLIC = [({'team': 'Динамо', 'played': '10', 'won': '6', 'drawn': '2', 'lost': '2'},
  {'team': 'Динамо', 'played': 10, 'won': 6, 'drawn': 2, 'lost': 2, 'points': 20}),
 ({'team': ' Шахтар ', 'played': '10', 'won': '5', 'drawn': '5', 'lost': '0'},
  {'team': 'Шахтар', 'played': 10, 'won': 5, 'drawn': 5, 'lost': 0, 'points': 20})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
