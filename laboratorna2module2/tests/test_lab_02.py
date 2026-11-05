"""Відкриті приклади 02 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(2)

PUBLIC = [({'sku': 'AB-1234',
   'name': 'Болт',
   'category': 'Метизи',
   'qty': '100',
   'unit_price': '2.5',
   'reorder': 'ні'},
  {'sku': 'AB-1234',
   'name': 'болт',
   'category': 'метизи',
   'qty': 100,
   'unit_price': 2.5,
   'reorder': False,
   'value': 250.0}),
 ({'sku': ' CD-5678 ',
   'name': 'Гайка',
   'category': 'метизи',
   'qty': '0',
   'unit_price': '1.2',
   'reorder': 'так'},
  {'sku': 'CD-5678',
   'name': 'гайка',
   'category': 'метизи',
   'qty': 0,
   'unit_price': 1.2,
   'reorder': True,
   'value': 0.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
