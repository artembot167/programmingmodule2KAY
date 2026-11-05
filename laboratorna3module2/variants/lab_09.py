"""Лабораторна робота 3. Задача 9: збереження датасету у CSV і JSON.

Правила — у student.md (розділ 7, задача 9) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_09.py
"""
import csv
import json
import os
from pathlib import Path


def save_dataset(records: list, folder, name: str, fields: list) -> dict:
    """Записує folder/name.csv і folder/name.json та повертає словник за правилами задачі 9."""
    raise NotImplementedError  # TODO: реалізуйте за описом задачі
