"""Відкриті приклади 26 (з картки). Повний набір перевірок — у викладача."""
import json
import pytest
from conftest import load

M = load(26)

PUBLIC = [({'title': 'Пісня 1', 'artist': 'Гурт А', 'genre': 'Рок', 'duration': '3:45', 'plays': '1000'},
  {'title': 'Пісня 1',
   'artist': 'Гурт А',
   'genre': 'рок',
   'duration': '3:45',
   'plays': 1000,
   'seconds': 225,
   'listened_s': 225000}),
 ({'title': ' Пісня 2 ', 'artist': 'Гурт Б', 'genre': 'рок', 'duration': '4:05', 'plays': '250'},
  {'title': 'Пісня 2',
   'artist': 'Гурт Б',
   'genre': 'рок',
   'duration': '4:05',
   'plays': 250,
   'seconds': 245,
   'listened_s': 61250})]


@pytest.mark.parametrize("raw,expected", PUBLIC)
def test_public(raw, expected):
    assert M.clean_record(raw) == expected


def test_functions_exist():
    for name in ('clean_record', 'load_csv', 'to_json_text', 'from_json_text', 'to_csv_text', 'convert', 'summarize'):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
