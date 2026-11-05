"""Лабораторна робота 3. Задача 10: повний конвеєр збору.

Правила — у student.md (розділ 7, задача 10) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_10.py
Усе потрібне для цієї задачі пишіть у цьому файлі: інші файли variants/ не імпортуйте.
"""
import time

import requests
from bs4 import BeautifulSoup


def run_pipeline(base, cfg, outdir, sleep=time.sleep, user_agent="StudyBot/1.0 (educational lab)",
                 max_pages=20) -> dict:
    """Збирає каталог сайту, чистить ціни, зберігає dataset.csv і dataset.json (правила задачі 10)."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
