"""Допоміжний завантажувач: підключає файл варіанта з теки variants/ (або з VARIANT_DIR)."""
import importlib.util
import os
import signal
from pathlib import Path
from types import SimpleNamespace

import pytest

import sites

ROOT = Path(__file__).resolve().parent


def load(number):
    """Повертає модуль варіанта з номером number."""
    base = Path(os.environ.get("VARIANT_DIR", ROOT.parent / "variants"))
    for prefix in ("variant", "lab", "task"):
        path = base / f"{prefix}_{number:02d}.py"
        if path.exists():
            spec = importlib.util.spec_from_file_location(f"{prefix}_{number:02d}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError(f"Не знайдено файл варіанта {number:02d} у {base}")


@pytest.fixture(autouse=True)
def _watchdog():
    """Тест, що завис (нескінченний цикл), завершується за 20 с."""
    def boom(signum, frame):
        raise TimeoutError("тест завис довше 20 с: перевірте умови завершення циклів")
    old = signal.signal(signal.SIGALRM, boom)
    signal.alarm(20)
    yield
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old)


@pytest.fixture
def env(tmp_path):
    """env.serve(ключ, **параметри) запускає тестовий сайт; env.tmp це тимчасова тека."""
    stops = []

    def serve(key, **opts):
        site, stop = sites.start_site(key, **opts)
        stops.append(stop)
        return site

    yield SimpleNamespace(serve=serve, tmp=tmp_path)
    for stop in stops:
        stop()
