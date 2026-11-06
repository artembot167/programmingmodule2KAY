"""Допоміжні засоби тестів: завантажувач варіанта, опис графіка та перевірка випадків.

Тести не відкривають вікон і не користуються мережею: сервіс перевіряється через TestClient,
а графік (бекенд Agg) порівнюється за властивостями об'єктів Matplotlib, а не за пікселями.
Щоб побачити властивості власного графіка, викличте figure_summary(fig).
"""
import copy
import importlib.util
import json
import math
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest
from fastapi.testclient import TestClient
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_hex
from matplotlib.patches import Rectangle, Wedge

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "data"


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


def load_sets(number):
    """Три набори даних задачі: словник {"S1": {"cfg": ..., "records": ...}, ...}."""
    with (DATA_DIR / f"task_{number:02d}.json").open(encoding="utf-8") as handle:
        return json.load(handle)


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


# ---------- опис графіка ----------
def _num(value):
    value = float(value)
    return None if math.isnan(value) else round(value, 4)


def axes_summary(ax):
    ax.figure.canvas.draw()
    rects = [p for p in ax.patches if isinstance(p, Rectangle)]
    wedges = [p for p in ax.patches if isinstance(p, Wedge)]
    legend = ax.get_legend()
    return {
        "title": ax.get_title(),
        "xlabel": ax.get_xlabel(),
        "ylabel": ax.get_ylabel(),
        "xticklabels": [t.get_text() for t in ax.get_xticklabels()],
        "yticklabels": [t.get_text() for t in ax.get_yticklabels()],
        "bar_lefts": [_num(p.get_x()) for p in rects],
        "bar_bottoms": [_num(p.get_y()) for p in rects],
        "bar_widths": [_num(p.get_width()) for p in rects],
        "bar_heights": [_num(p.get_height()) for p in rects],
        "bar_colors": [to_hex(p.get_facecolor()) for p in rects],
        "lines": [{"x": [_num(v) for v in ln.get_xdata()], "y": [_num(v) for v in ln.get_ydata()],
                   "label": ln.get_label(), "marker": ln.get_marker(), "linestyle": ln.get_linestyle(),
                   "color": to_hex(ln.get_color())} for ln in ax.lines],
        "points": [[_num(a), _num(b)] for c in ax.collections if hasattr(c, "get_offsets")
                   and not isinstance(c, PolyCollection) for a, b in c.get_offsets().tolist()],
        "wedges": [_num(abs(w.theta2 - w.theta1) / 360) for w in wedges],
        "texts": [t.get_text() for t in ax.texts],
        "legend": [t.get_text() for t in legend.get_texts()] if legend else [],
        "yinverted": bool(ax.yaxis_inverted()),
        "fills": sum(isinstance(c, PolyCollection) for c in ax.collections),
    }


def figure_summary(fig):
    """Властивості малюнка: напис над усім малюнком і список осей з їхніми властивостями."""
    sup = fig._suptitle.get_text() if getattr(fig, "_suptitle", None) is not None else ""
    return {"suptitle": sup, "axes": [axes_summary(ax) for ax in fig.axes]}


def match(actual, expected, path="графік"):
    """Порівнює опис графіка з очікуванням: у словнику перевіряються лише ключі з очікування."""
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: очікувався словник"
        for key, value in expected.items():
            assert key in actual, f"{path}: немає ключа {key}"
            match(actual[key], value, f"{path}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list) and len(actual) == len(expected), \
            f"{path}: очікувано {expected}, отримано {actual}"
        for i, (a, e) in enumerate(zip(actual, expected)):
            match(a, e, f"{path}[{i}]")
    elif isinstance(expected, bool) or expected is None or isinstance(expected, str):
        assert actual == expected, f"{path}: очікувано {expected!r}, отримано {actual!r}"
    else:
        assert actual is not None and math.isclose(actual, expected, abs_tol=1e-6), \
            f"{path}: очікувано {expected}, отримано {actual}"


# ---------- виконання випадків ----------
class CountingClient:
    """Обгортка над TestClient, що рахує звернення до сервісу."""

    def __init__(self, inner):
        self.inner = inner
        self.count = 0

    def get(self, *args, **kwargs):
        self.count += 1
        return self.inner.get(*args, **kwargs)


class FakeResponse:
    def __init__(self, status, body):
        self.status_code = status
        self._body = body

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeClient:
    """Клієнт-заглушка, що завжди відповідає заданим кодом і тілом."""

    def __init__(self, status, body):
        self.status, self.body, self.count = status, body, 0

    def get(self, *args, **kwargs):
        self.count += 1
        return FakeResponse(self.status, self.body)


def _setup(number, case):
    data = load_sets(number)[case["set"]]
    cfg = {**data["cfg"], **case.get("cfg_patch", {})}
    records = copy.deepcopy(case["records"] if "records" in case else data["records"])
    return cfg, records


def run_case(number, case):
    module = load(number)
    cfg, records = _setup(number, case)
    kind = case["kind"]
    if kind == "api":
        before = copy.deepcopy(records)
        client = TestClient(module.create_app(records, cfg))
        for method, url, body, status, expected in case["steps"]:
            response = client.request(method, url, json=body)
            assert response.status_code == status, \
                f"{method} {url}: код {response.status_code}, очікувався {status}; тіло: {response.text[:200]}"
            if expected is not None:
                assert response.json() == expected, \
                    f"{method} {url}: очікувано {expected}, отримано {response.json()}"
        assert records == before, "create_app не повинна змінювати передані записи"
    elif kind == "fig":
        payload = case["payload"]
        before = copy.deepcopy(payload)
        fig = module.build_figure(payload, cfg)
        assert payload == before, "build_figure не повинна змінювати передані дані"
        match(figure_summary(fig), case["expect"])
    elif kind in ("pipe", "fake"):
        if kind == "pipe":
            client = CountingClient(TestClient(module.create_app(records, cfg)))
        else:
            client = FakeClient(case["status"], case.get("json"))
        if "error" in case:
            with pytest.raises(RuntimeError) as info:
                module.chart_from_service(client, cfg)
            assert str(info.value) == case["error"]
            return
        fig = module.chart_from_service(client, cfg)
        match(figure_summary(fig), case["expect"])
        if "requests" in case:
            assert client.count == case["requests"], \
                f"сервісу надіслано {client.count} запитів, очікувалося {case['requests']}"
    else:
        raise ValueError(kind)
