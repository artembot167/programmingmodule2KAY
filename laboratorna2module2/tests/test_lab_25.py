"""Відкриті приклади 25 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(25)

PUBLIC = [({'task': 'Макет', 'assignee': 'Анна', 'priority': 'Високий', 'est_h': '8', 'spent_h': '10.5'},
  {'task': 'Макет',
   'assignee': 'Анна',
   'priority': 'високий',
   'est_h': 8.0,
   'spent_h': 10.5,
   'delta_h': 2.5}),
 ({'task': ' API ', 'assignee': 'Богдан', 'priority': 'середній', 'est_h': '16', 'spent_h': '12'},
  {'task': 'API',
   'assignee': 'Богдан',
   'priority': 'середній',
   'est_h': 16.0,
   'spent_h': 12.0,
   'delta_h': -4.0})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
