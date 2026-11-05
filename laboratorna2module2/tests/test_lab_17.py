"""Відкриті приклади 17 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(17)

PUBLIC = [({'author': 'Анна', 'topic': 'Музика', 'likes': '120', 'comments': '15', 'reposts': '4'},
  {'author': 'Анна',
   'topic': 'музика',
   'likes': 120,
   'comments': 15,
   'reposts': 4,
   'engagement': 162}),
 ({'author': ' Богдан ', 'topic': 'музика', 'likes': '10', 'comments': '2', 'reposts': '0'},
  {'author': 'Богдан',
   'topic': 'музика',
   'likes': 10,
   'comments': 2,
   'reposts': 0,
   'engagement': 14})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
