"""Допоміжні засоби тестів: завантажувач варіанта, локальний API і перевірка загальних угод.

Файл не змінюйте. Тести не залежать від інтернету: API піднімається на 127.0.0.1 для кожного тесту.
"""
import importlib.util
import os
import socket
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parent
VARIANT_DIR = Path(os.environ.get("VARIANT_DIR", ROOT.parent / "variants"))

for _candidate in (ROOT.parent / "server", ROOT.parent.parent / "starter" / "server"):
    if (_candidate / "open_api.py").exists():
        sys.path.insert(0, str(_candidate))
        break

from open_api import run_api  # noqa: E402


def load(number):
    """Повертає модуль варіанта з номером number."""
    base = Path(os.environ.get("VARIANT_DIR", VARIANT_DIR))
    for prefix in ("variant", "lab", "task"):
        path = base / f"{prefix}_{number:02d}.py"
        if path.exists():
            spec = importlib.util.spec_from_file_location(f"{prefix}_{number:02d}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError(f"Не знайдено файл варіанта {number:02d} у {base}")


@pytest.fixture
def api():
    """Свіжий локальний сервер для одного тесту (дані й лічильники починаються спочатку)."""
    with run_api() as server:
        yield server


@pytest.fixture
def spy(monkeypatch):
    """Записує значення timeout кожного запиту, відправленого через requests."""
    seen = []
    original = requests.adapters.HTTPAdapter.send

    def send(self, request, **kwargs):
        seen.append(kwargs.get("timeout"))
        return original(self, request, **kwargs)

    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", send)
    return seen


def check_conventions(api, spy):
    """Загальні угоди: кожен запит іде через requests, має timeout, Accept і User-Agent."""
    assert len(spy) >= len(api.log), "Запити мають іти через бібліотеку requests"
    assert all(t is not None for t in spy), "Кожен запит має мати timeout (зараз хоч один без нього)"
    for entry in api.log:
        headers = entry["headers"]
        assert "application/json" in headers.get("accept", ""), "Додайте заголовок Accept: application/json"
        assert headers.get("user-agent", "").startswith("pp-p05"), "Додайте заголовок User-Agent: pp-p05-student"


def free_port():
    """Порт, на якому ніхто не слухає: підходить для перевірки помилки з'єднання."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def raises(exc_type, text, func):
    """Перевіряє тип і точний текст винятку."""
    with pytest.raises(exc_type) as info:
        func()
    assert str(info.value) == text
