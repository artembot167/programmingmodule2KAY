"""Відкриті приклади 24 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(24)

PUBLIC = [({'teacher': 'Коваль О.',
   'subject': 'Python',
   'room': '201',
   'pairs_per_week': '4',
   'students': '30'},
  {'teacher': 'Коваль О.',
   'subject': 'python',
   'room': '201',
   'pairs_per_week': 4,
   'students': 30,
   'hours': 8}),
 ({'teacher': ' Коваль О. ',
   'subject': 'python',
   'room': '202',
   'pairs_per_week': '2',
   'students': '25'},
  {'teacher': 'Коваль О.',
   'subject': 'python',
   'room': '202',
   'pairs_per_week': 2,
   'students': 25,
   'hours': 4})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
