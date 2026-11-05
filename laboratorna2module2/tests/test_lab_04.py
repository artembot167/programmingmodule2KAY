"""Відкриті приклади 04 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(4)

PUBLIC = [({'date': '05.03', 'category': 'Їжа', 'amount': '120.5', 'method': 'картка'},
  {'date': '05.03', 'category': 'їжа', 'amount': 120.5, 'method': 'картка', 'is_card': True}),
 ({'date': ' 06.03 ', 'category': 'їжа', 'amount': '80', 'method': 'готівка'},
  {'date': '06.03', 'category': 'їжа', 'amount': 80.0, 'method': 'готівка', 'is_card': False})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
