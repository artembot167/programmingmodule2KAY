"""Допоміжні функції перевірок: розбір HTML і CSS, контраст кольорів, запуск скриптів у тестовому DOM."""
import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def load_sites():
    for cand in (HERE / "data" / "sites.json", HERE.parent / "data" / "sites.json"):
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
    raise FileNotFoundError("Не знайдено data/sites.json")


def soup(markup):
    return BeautifulSoup(markup, "html.parser")


def text(node):
    return " ".join(node.get_text(" ").split())


# ---------------------------------------------------------------- HTML
class _Validator(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.problems, self.ids, self.roots, self.stray = [], [], [], [], []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if k == "id":
                self.ids.append(v)
        if not self.stack:
            self.roots.append(tag)
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        for k, v in attrs:
            if k == "id":
                self.ids.append(v)
        if not self.stack:
            self.roots.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.problems.append(f"зайвий або невчасний закриваючий тег </{tag}>")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()

    def handle_data(self, data):
        if not self.stack and data.strip():
            self.stray.append(data.strip())


def inspect_markup(markup):
    v = _Validator()
    v.feed(markup)
    v.close()
    problems = list(v.problems)
    if v.stack:
        problems.append("не закрито теги: " + ", ".join(v.stack))
    dup = sorted({i for i in v.ids if v.ids.count(i) > 1})
    if dup:
        problems.append("повторні id: " + ", ".join(dup))
    return v, problems


def validate_markup(markup):
    return inspect_markup(markup)[1]


def fragment_roots(markup):
    v, _ = inspect_markup(markup)
    return v.roots


# ---------------------------------------------------------------- кольори
def _lum(hex_color):
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# ---------------------------------------------------------------- CSS
def norm_selector(sel):
    sel = re.sub(r"\[\s*([\w-]+)\s*([~|^$*]?=)\s*([\"']?)([^\]\"']*)\3\s*\]", r"[\1\2\4]", sel.strip())
    sel = re.sub(r"\s*([>+~,])\s*", r" \1 ", sel)
    sel = re.sub(r"\s+", " ", sel).strip()
    return sel.replace(" , ", ", ")


def norm_value(value):
    v = re.sub(r"\s*!important\s*$", "", value.strip().lower())
    v = re.sub(r"\s+", " ", v)
    v = re.sub(r"\s*,\s*", ", ", v)
    v = re.sub(r"(?<![\d.])0(?:px|rem|em)\b", "0", v)
    return v


class Rule:
    def __init__(self, selectors, decls, media=None, raw_decls=None):
        self.selectors, self.decls, self.media = selectors, decls, media
        self.raw = raw_decls or []


def parse_css(css):
    """Повертає (rules, problems). Підтримує вкладені @media."""
    problems = []
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    if css.count("{") != css.count("}"):
        problems.append("кількість { і } не збігається")
    rules, i, n = [], 0, len(css)

    def block(start, media):
        nonlocal problems
        pos = start
        while pos < n:
            while pos < n and css[pos].isspace():
                pos += 1
            if pos >= n or css[pos] == "}":
                return pos + 1
            brace = css.find("{", pos)
            if brace == -1:
                if css[pos:].strip():
                    problems.append("зайвий текст поза правилами")
                return n
            head = css[pos:brace].strip()
            if head.startswith("@media"):
                pos = block(brace + 1, norm_value(head[6:].strip()))
                continue
            end = css.find("}", brace)
            if end == -1:
                problems.append("не закрито блок правила")
                return n
            body = css[brace + 1:end]
            decls, raw = {}, []
            for d in [x for x in body.split(";") if x.strip()]:
                if ":" not in d:
                    problems.append(f"оголошення без двокрапки: «{d.strip()}»")
                    continue
                k, v = d.split(":", 1)
                decls[k.strip().lower()] = norm_value(v)
                raw.append((k.strip().lower(), v.strip()))
            sels = [norm_selector(s) for s in head.split(",") if s.strip()]
            rules.append(Rule(sels, decls, media, raw))
            pos = end + 1
        return pos

    block(0, None)
    return rules, problems


def decls_for(rules, selector, media=None):
    out = {}
    target = norm_selector(selector)
    for r in rules:
        if r.media == media and target in r.selectors:
            out.update(r.decls)
    return out


# ---------------------------------------------------------------- JS
FAKEDOM = HERE / "fakedom.js"
NODE = shutil.which("node")


def run_js(code, elements, scenario):
    """Виконує скрипт у тестовому DOM і повертає JSON-результат сценарію (JS-код у рядку)."""
    if NODE is None:
        pytest.skip("node не встановлено: JS-перевірки пропущено")
    payload = json.dumps({"code": code, "elements": elements, "scenario": scenario})
    proc = subprocess.run([NODE, str(FAKEDOM)], input=payload, capture_output=True, text=True, timeout=20)
    if proc.returncode != 0:
        raise AssertionError((proc.stderr or "скрипт завершився з помилкою").strip().splitlines()[0])
    return json.loads(proc.stdout or "null")
