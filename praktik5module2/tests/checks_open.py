"""Відкриті перевірки: однакові для студента й викладача. Кожна перевірка отримує модуль варіанта й опис сайту."""
import copy
import json
import re
from html import escape

import pytest
from bs4 import BeautifulSoup

from helpers import (decls_for, fragment_roots, norm_selector, parse_css, run_js, soup, text,
                     validate_markup)

FUNCS = {1: "build_page", 2: "build_nav", 3: "build_sections", 4: "build_price_table", 5: "build_gallery",
         6: "build_contact_form", 7: "build_base_css", 8: "build_selector_css", 9: "build_menu_script",
         10: "build_form_script"}

OPEN = {n: [] for n in range(1, 11)}
OPEN_ERRORS = {n: [] for n in range(1, 11)}


def reg(n):
    def deco(fn):
        OPEN[n].append(fn)
        return fn
    return deco


def out(M, n, site):
    result = getattr(M, FUNCS[n])(copy.deepcopy(site))
    assert isinstance(result, str), "функція має повертати рядок (str)"
    assert result.strip(), "функція повернула порожній рядок"
    return result


def ok_markup(markup):
    problems = validate_markup(markup)
    assert not problems, "розмітка містить помилки: " + "; ".join(problems)


def drop(site, key):
    d = copy.deepcopy(site)
    d.pop(key, None)
    return d


def error_case(n, label, make_site, message):
    OPEN_ERRORS[n].append((label, make_site, message))


# ======================================================================= Задача 1. Каркас сторінки
@reg(1)
def t01_doctype_and_lang(M, site):
    html = out(M, 1, site)
    assert html.lstrip().lower().startswith("<!doctype html>"), "документ має починатися з <!DOCTYPE html>"
    assert soup(html).html is not None and soup(html).html.get("lang") == site["lang"], "у <html> потрібен lang"


@reg(1)
def t01_head_meta(M, site):
    s = soup(out(M, 1, site))
    meta = s.head.find("meta", attrs={"charset": True})
    assert meta and meta["charset"].lower() == "utf-8", "потрібен <meta charset=\"utf-8\">"
    assert s.head.title is not None and s.head.title.get_text() == site["title"], "<title> має дорівнювати назві сайту"


@reg(1)
def t01_assets(M, site):
    s = soup(out(M, 1, site))
    link = s.head.find("link", attrs={"rel": "stylesheet"})
    assert link and link.get("href") == "style.css", "потрібен <link rel=\"stylesheet\" href=\"style.css\"> у <head>"
    script = s.head.find("script", attrs={"src": "script.js"})
    assert script is not None, "потрібен <script src=\"script.js\" defer> у <head>"
    assert script.has_attr("defer"), "скрипт має мати атрибут defer"


@reg(1)
def t01_landmarks(M, site):
    body = soup(out(M, 1, site)).body
    tags = [c.name for c in body.children if getattr(c, "name", None)]
    assert tags == ["header", "main", "footer"], f"у <body> очікується header, main, footer; знайдено {tags}"
    assert body.main.get("id") == "content", "у <main> потрібен id=\"content\""


@reg(1)
def t01_heading(M, site):
    s = soup(out(M, 1, site))
    h1 = s.find_all("h1")
    assert len(h1) == 1, f"на сторінці має бути один <h1>, знайдено {len(h1)}"
    assert h1[0].get_text() == site["title"] and h1[0].find_parent("header"), "<h1> з назвою сайту має бути в <header>"
    tag = s.header.find("p", class_="tagline")
    assert tag is not None and tag.get_text() == site["tagline"], "у <header> потрібен <p class=\"tagline\"> з гаслом"


@reg(1)
def t01_well_formed(M, site):
    ok_markup(out(M, 1, site))


error_case(1, "немає title", lambda s: drop(s, "title"), "Немає поля: title")
error_case(1, "порожня назва", lambda s: dict(copy.deepcopy(s), title="   "), "Порожня назва сайту")


# ======================================================================= Задача 2. Навігація
def nav_links(markup):
    return [(a.get("href"), a.get_text()) for a in soup(markup).select("nav > ul > li > a")]


@reg(2)
def t02_single_nav(M, site):
    html = out(M, 2, site)
    assert fragment_roots(html) == ["nav"], f"фрагмент має містити один кореневий <nav>, знайдено {fragment_roots(html)}"
    nav = soup(html).nav
    assert nav.get("id") == "site-nav", "у <nav> потрібен id=\"site-nav\""


@reg(2)
def t02_links(M, site):
    expected = [(f"#{s['id']}", s["title"]) for s in site["sections"]] + [("#contact", "Зв'язок")]
    assert nav_links(out(M, 2, site)) == expected, "посилання меню мають відповідати розділам за порядком, останнє — #contact"


@reg(2)
def t02_list_structure(M, site):
    nav = soup(out(M, 2, site)).nav
    lists = nav.find_all("ul")
    assert len(lists) == 1 and lists[0].parent is nav, "у <nav> має бути один <ul>"
    items = lists[0].find_all(recursive=False)
    assert all(i.name == "li" and len(i.find_all("a")) == 1 for i in items), "кожен <li> містить рівно одне посилання"
    assert len(items) == len(site["sections"]) + 1


@reg(2)
def t02_well_formed(M, site):
    ok_markup(out(M, 2, site))


error_case(2, "немає розділів", lambda s: dict(copy.deepcopy(s), sections=[]), "Немає розділів")
error_case(2, "id з великої літери", lambda s: dict(copy.deepcopy(s), sections=[{"id": "About", "title": "Т", "paragraphs": []}]),
           "Некоректний id: About")


# ======================================================================= Задача 3. Розділи
@reg(3)
def t03_sections_roots(M, site):
    html = out(M, 3, site)
    assert fragment_roots(html) == ["article"] * len(site["sections"]), "кожен розділ — окремий кореневий <article>"
    ids = [s.get("id") for s in soup(html).find_all("article", recursive=False)]
    assert ids == [s["id"] for s in site["sections"]], "id розділів і їхній порядок мають збігатися з вхідними"
    assert all("section" in s.get("class", []) for s in soup(html).find_all("article", recursive=False)), "потрібен class=\"section\""


@reg(3)
def t03_headings(M, site):
    secs = soup(out(M, 3, site)).find_all("article", recursive=False)
    for sec, src in zip(secs, site["sections"]):
        h2 = sec.find("h2")
        assert h2 is not None and h2.get_text() == src["title"], f"розділ {src['id']}: потрібен <h2> із заголовком"


@reg(3)
def t03_paragraphs(M, site):
    secs = soup(out(M, 3, site)).find_all("article", recursive=False)
    for sec, src in zip(secs, site["sections"]):
        got = [p.get_text() for p in sec.find_all("p", recursive=False)]
        assert got == src.get("paragraphs", []), f"розділ {src['id']}: абзаци не збігаються"


@reg(3)
def t03_facts(M, site):
    secs = soup(out(M, 3, site)).find_all("article", recursive=False)
    for sec, src in zip(secs, site["sections"]):
        lists = sec.find_all("ul")
        if src.get("facts"):
            assert len(lists) == 1 and "facts" in lists[0].get("class", []), f"розділ {src['id']}: потрібен <ul class=\"facts\">"
            assert [li.get_text() for li in lists[0].find_all("li")] == src["facts"]
        else:
            assert not lists, f"розділ {src['id']}: без фактів список не потрібен"


@reg(3)
def t03_well_formed(M, site):
    ok_markup(out(M, 3, site))


error_case(3, "порожній заголовок", lambda s: dict(copy.deepcopy(s), sections=[{"id": "about", "title": "  ", "paragraphs": []}]),
           "Порожній заголовок: about")
error_case(3, "немає розділів", lambda s: drop(s, "sections"), "Немає розділів")


# ======================================================================= Задача 4. Таблиця цін
def price_text(value):
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.2f}".replace(".", ",")


@reg(4)
def t04_caption_and_head(M, site):
    t = soup(out(M, 4, site)).table
    assert t is not None and "price-table" in t.get("class", []), "потрібна <table class=\"price-table\">"
    assert t.caption is not None and t.caption.get_text() == f"Ціни: {site['title']}", "caption: «Ціни: назва сайту»"
    assert [c.name for c in t.find_all(recursive=False)] == ["caption", "thead", "tbody"], "у таблиці: caption, thead, tbody"
    heads = [th.get_text() for th in t.thead.find_all("th")]
    assert heads == ["Назва", "Примітка", "Ціна, грн"], "заголовки стовпців: Назва, Примітка, Ціна, грн"


@reg(4)
def t04_rows(M, site):
    t = soup(out(M, 4, site)).table
    rows = t.tbody.find_all("tr", recursive=False)
    assert len(rows) == len(site["items"]), "рядків у <tbody> має бути стільки, скільки позицій"
    for row, item in zip(rows, site["items"]):
        tds = row.find_all("td", recursive=False)
        assert [td.get_text() for td in tds] == [item["name"], item["note"], price_text(item["price"])], \
            f"{item['name']}: назва, примітка й ціна у трьох <td>"
        assert "num" in tds[2].get("class", []), "ціна — у <td class=\"num\">"


@reg(4)
def t04_average(M, site):
    p = soup(out(M, 4, site)).find("p", class_="average")
    avg = round(sum(i["price"] for i in site["items"]) / len(site["items"]), 2)
    assert p is not None and p.get_text() == f"Середня ціна: {price_text(avg)} грн", \
        f"після таблиці потрібен <p class=\"average\">Середня ціна: {price_text(avg)} грн</p>"


@reg(4)
def t04_well_formed(M, site):
    html = out(M, 4, site)
    assert fragment_roots(html) == ["table", "p"], "фрагмент: таблиця, а за нею абзац із середньою ціною"
    ok_markup(html)


error_case(4, "немає позицій", lambda s: dict(copy.deepcopy(s), items=[]), "Немає позицій")
error_case(4, "від'ємна ціна", lambda s: dict(copy.deepcopy(s), items=[{"name": "Чай", "note": "", "price": -1}]),
           "Некоректна ціна: Чай")


# ======================================================================= Задача 5. Галерея
@reg(5)
def t05_container(M, site):
    html = out(M, 5, site)
    assert fragment_roots(html) == ["article"]
    art = soup(html).article
    assert art.get("id") == "gallery"
    h2 = art.find("h2")
    assert h2 is not None and h2.get_text() == "Галерея"
    assert len(art.select("div.gallery > div.photo")) == len(site["gallery"]), "блоки <div class=\"photo\"> мають лежати в <div class=\"gallery\">"


@reg(5)
def t05_images(M, site):
    photos = soup(out(M, 5, site)).select("div.gallery > div.photo")
    for photo, src in zip(photos, site["gallery"]):
        img = photo.find("img")
        assert img is not None and img.get("src") == f"img/{src['file']}", f"{src['file']}: src має бути img/назва"
        assert img.get("alt") == src["alt"], f"{src['file']}: alt не збігається"


@reg(5)
def t05_captions(M, site):
    photos = soup(out(M, 5, site)).select("div.gallery > div.photo")
    assert [p.find("p", class_="caption").get_text() for p in photos] == [g["caption"] for g in site["gallery"]], \
        "підпис — <p class=\"caption\"> у тому ж блоці"


@reg(5)
def t05_well_formed(M, site):
    ok_markup(out(M, 5, site))


error_case(5, "порожня галерея", lambda s: dict(copy.deepcopy(s), gallery=[]), "Галерея порожня")
error_case(5, "порожній alt",
           lambda s: dict(copy.deepcopy(s), gallery=[{"file": "a.jpg", "alt": " ", "caption": "A", "width": 10, "height": 10}]),
           "Немає опису (alt) для: a.jpg")


# ======================================================================= Задача 6. Форма
@reg(6)
def t06_form_attrs(M, site):
    html = out(M, 6, site)
    assert fragment_roots(html) == ["article"]
    sec = soup(html).article
    assert sec.get("id") == "contact"
    assert sec.find("h2").get_text() == "Зв'язок"
    form = sec.find("form")
    assert form is not None and form.get("id") == "contact-form" and form.get("method") == "post" and form.get("action") == "#"


@reg(6)
def t06_fields(M, site):
    form = soup(out(M, 6, site)).form
    blocks = form.find_all("div", class_="field", recursive=False)
    assert len(blocks) == len(site["fields"])
    for block, f in zip(blocks, site["fields"]):
        label = block.find("label")
        assert label is not None and label.get_text() == f["label"] and label.get("for") == f"f-{f['name']}", f"{f['name']}: label for"
        control = block.find(["input", "textarea"])
        assert control is not None and control.get("id") == f"f-{f['name']}" and control.get("name") == f["name"], f"{f['name']}: id і name"
        if f["type"] == "textarea":
            assert control.name == "textarea" and control.get("rows") == "4"
        else:
            assert control.name == "input" and control.get("type") == f["type"], f"{f['name']}: type"


@reg(6)
def t06_button_and_message(M, site):
    form = soup(out(M, 6, site)).form
    btn = form.find("button")
    assert btn is not None and btn.get("type") == "submit" and btn.get_text() == "Надіслати"
    msg = form.find("p", id="form-message")
    assert msg is not None and msg.get_text() == "", "потрібен порожній <p id=\"form-message\">"


@reg(6)
def t06_well_formed(M, site):
    ok_markup(out(M, 6, site))


error_case(6, "немає полів", lambda s: dict(copy.deepcopy(s), fields=[]), "Немає полів")
error_case(6, "невідомий тип",
           lambda s: dict(copy.deepcopy(s), fields=[{"name": "x", "label": "X", "type": "date", "required": False}]),
           "Невідомий тип поля: date")


# ======================================================================= Задача 7. Базові стилі
def css_rules(M, n, site):
    css = out(M, n, site)
    rules, problems = parse_css(css)
    assert not problems, "помилки в CSS: " + "; ".join(problems)
    return css, rules


@reg(7)
def t07_box_sizing(M, site):
    _, rules = css_rules(M, 7, site)
    got = [r.decls.get("box-sizing") for r in rules if "*" in r.selectors]
    assert "border-box" in got, "правило для * має задавати box-sizing: border-box"


@reg(7)
def t07_body(M, site):
    _, rules = css_rules(M, 7, site)
    body = decls_for(rules, "body")
    p = site["palette"]
    assert body.get("margin") == "0", "body: margin: 0"
    assert "sans-serif" in body.get("font-family", ""), "body: font-family із запасним sans-serif"
    assert body.get("color") == p["text"].lower() and body.get("background-color") == p["bg"].lower(), \
        "body: color — колір тексту, background-color — колір тла з палітри"
    lh = body.get("line-height", "")
    assert re.fullmatch(r"\d+(\.\d+)?", lh) and float(lh) >= 1.4, "body: line-height — число не менше 1.4"


@reg(7)
def t07_links_and_header(M, site):
    _, rules = css_rules(M, 7, site)
    p = site["palette"]
    assert decls_for(rules, "a").get("color") == p["accent"].lower(), "a: колір акценту"
    assert decls_for(rules, "header a").get("color") == p["bg"].lower(), "header a: посилання в шапці мають колір тла (інакше їх не видно на акценті)"
    assert decls_for(rules, "h2").get("color") == p["accent"].lower(), "h2: колір акценту"
    header = decls_for(rules, "header")
    assert header.get("background-color") == p["accent"].lower() and header.get("color") == p["bg"].lower(), \
        "header: фон — акцент, текст — колір тла"


@reg(7)
def t07_only_palette_colors(M, site):
    _, rules = css_rules(M, 7, site)
    allowed = {v.lower() for v in site["palette"].values()}
    for r in rules:
        for prop, value in r.decls.items():
            for color in re.findall(r"#[0-9a-f]{3,8}\b|\brgba?\(", value):
                assert color in allowed, f"{r.selectors[0]}: колір «{color}» не з палітри сайту"


error_case(7, "немає palette", lambda s: drop(s, "palette"), "Немає поля: palette")
error_case(7, "коротка форма кольору",
           lambda s: dict(copy.deepcopy(s), palette={"bg": "#fff", "text": "#000000", "accent": "#0000ff"}),
           "Некоректний колір: bg")


# ======================================================================= Задача 8. Селектори
FIXTURE = """<body><header><h1>Заголовок</h1><p class="tagline">Гасло</p></header>
<nav id="site-nav"><ul><li><a href="#a">Один</a></li><li><a href="#b">Два</a></li></ul></nav>
<main id="content">
<article id="a" class="section"><h2>Перший</h2><p>Текст після заголовка.</p><p>Другий абзац.</p>
<ul class="facts"><li>Перше</li><li>Друге</li><li>Третє</li></ul><h3>Підзаголовок</h3><p>Ще текст.</p></article>
<article id="b" class="section"><h2>Другий</h2><p>Абзац.</p><ul><li>Звичайний список</li></ul></article>
<table class="price-table"><caption>Ціни</caption>
<thead><tr><th>Назва</th><th>Примітка</th><th>Ціна</th></tr></thead>
<tbody><tr><td>А</td><td>x</td><td class="num">1</td></tr><tr><td>Б</td><td>y</td><td class="num">2</td></tr>
<tr><td>В</td><td>z</td><td class="num">3</td></tr><tr><td>Г</td><td>w</td><td class="num">4</td></tr></tbody></table>
<p class="average">Середня ціна: 2,5 грн</p>
<article id="gallery"><h2>Галерея</h2><div class="gallery"><div class="photo"><img src="a.jpg" alt="а"><p class="caption">а</p></div>
<div class="photo"><img src="b.jpg" alt="б"><p class="caption">б</p></div></div></article>
<article id="contact"><h2>Зв'язок</h2><form id="contact-form"><div class="field"><label for="f-name">Ім'я</label><input type="text" id="f-name"></div>
<div class="field"><label for="f-note">Нотатка</label><textarea id="f-note"></textarea></div><button type="submit">Надіслати</button></form></article>
</main><footer><p>Підвал</p></footer></body>"""
FIX = BeautifulSoup(FIXTURE, "html.parser")
DYNAMIC = re.compile(r"::?(?:hover|focus-visible|focus-within|focus|active|visited|before|after|marker)\b")


def match_set(selector):
    """Множина елементів фікстури, які вибирає селектор (динамічні псевдокласи відкидаються)."""
    bare = DYNAMIC.sub("", selector).strip()
    bare = bare or "*"
    try:
        return frozenset(id(e) for e in FIX.select(bare))
    except Exception:
        return frozenset()


def requirement(rules, target, props, dyn=None, media=None):
    want = match_set(target)
    assert want, f"внутрішня помилка: ціль {target} порожня"
    for prop, pred in props.items():
        covered = set()
        for r in rules:
            if r.media != media or prop not in r.decls or not pred(r.decls[prop]):
                continue
            sets = []
            for sel in r.selectors:
                if dyn and dyn not in sel:
                    sets = None
                    break
                sets.append(match_set(sel))
            if not sets:
                continue
            union = set().union(*sets)
            if union and union <= want:
                covered |= union
        assert covered == set(want), f"немає правила лише для потрібних елементів зі значенням властивості {prop} (ціль: {target})"


def eq(*values):
    return lambda v: re.sub(r"\s", "", v) in {re.sub(r"\s", "", x) for x in values}


def has(word):
    return lambda v: word in v


def css8(M, site):
    css = out(M, 8, site)
    rules, problems = parse_css(css)
    assert not problems, "помилки в CSS: " + "; ".join(problems)
    assert "!important" not in css, "!important заборонено"
    return rules


@reg(8)
def t08_headings_and_paragraphs(M, site):
    rules = css8(M, site)
    requirement(rules, "h1, h2, h3", {"font-family": has("serif")})
    requirement(rules, "article > p", {"margin-top": eq("0")})


@reg(8)
def t08_nav(M, site):
    rules = css8(M, site)
    requirement(rules, "nav ul", {"display": eq("flex"), "margin": eq("0"), "padding": eq("0"), "list-style": eq("none")})
    requirement(rules, "nav li", {"margin-right": eq("1rem")})
    requirement(rules, "nav a", {"text-decoration": eq("none")})


@reg(8)
def t08_table(M, site):
    rules = css8(M, site)
    accent, bg = site["palette"]["accent"].lower(), site["palette"]["bg"].lower()
    requirement(rules, "table", {"width": eq("100%"), "border-collapse": eq("collapse")})
    requirement(rules, "td, th", {"padding": eq("8px"), "border": eq(f"1px solid {accent}")})
    requirement(rules, "thead th", {"background-color": eq(accent), "color": eq(bg), "text-align": eq("left")})


@reg(8)
def t08_table_details(M, site):
    rules = css8(M, site)
    requirement(rules, "tbody tr:nth-of-type(even)", {"background-color": eq("#f0f0f0")})
    requirement(rules, "td.num", {"text-align": eq("right")})


@reg(8)
def t08_facts_gallery_form(M, site):
    rules = css8(M, site)
    accent = site["palette"]["accent"].lower()
    requirement(rules, ".facts li:nth-of-type(1)", {"font-weight": eq("700", "bold")})
    requirement(rules, ".gallery", {"display": eq("flex")})
    requirement(rules, ".photo", {"margin-right": eq("1rem")})
    requirement(rules, ".gallery img", {"max-width": eq("100%"), "height": eq("auto"), "padding": eq("4px"),
                                         "border": eq(f"1px solid {accent}")})
    requirement(rules, ".field label", {"display": eq("block")})
    requirement(rules, "#contact-form input, #contact-form textarea", {"border": eq(f"2px solid {accent}")})


error_case(8, "немає palette", lambda s: drop(s, "palette"), "Немає поля: palette")
error_case(8, "некоректний колір", lambda s: dict(copy.deepcopy(s), palette={"bg": "#ffffff", "accent": "синій"}),
           "Некоректний колір: accent")


# ======================================================================= Задача 9. Скрипт меню
MENU_ELEMENTS = [
    {"id": "menu-toggle", "tag": "button", "text": "???"},
    {"id": "site-nav", "tag": "nav"},
    {"id": "nav-link", "tag": "a", "attrs": {"href": "#a"}},
]
MENU_SNAP = """const t = env.$("menu-toggle"), n = env.$("site-nav");
const snap = () => ({open: n.classList.contains("open"), label: t.textContent});
"""


def menu(M, site, scenario, elements=None):
    code = out(M, 9, site)
    return run_js(code, MENU_ELEMENTS if elements is None else elements, MENU_SNAP + scenario)


@reg(9)
def t09_initial_state(M, site):
    state = menu(M, site, "return snap();")
    assert state == {"open": False, "label": site["menu_open"]}, \
        f"після завантаження меню закрите (без класу open), підпис «{site['menu_open']}»; отримано {state}"


@reg(9)
def t09_toggle(M, site):
    log = menu(M, site, 'const l = []; env.fire(t, "click"); l.push(snap()); env.fire(t, "click"); l.push(snap()); return l;')
    assert log[0] == {"open": True, "label": site["menu_close"]}, f"перший клік відкриває меню: {log[0]}"
    assert log[1] == {"open": False, "label": site["menu_open"]}, f"другий клік закриває меню: {log[1]}"


@reg(9)
def t09_escape(M, site):
    log = menu(M, site, 'env.fire(t, "click"); env.key("Escape"); return snap();')
    assert log == {"open": False, "label": site["menu_open"]}, "Escape має закривати відкрите меню"


@reg(9)
def t09_link_click(M, site):
    log = menu(M, site, 'env.fire(t, "click"); env.fire(n, "click", {target: env.$("nav-link")}); return snap();')
    assert log["open"] is False and log["label"] == site["menu_open"], "клік по посиланню в меню має закривати його"


error_case(9, "немає підпису", lambda s: drop(s, "menu_open"), "Немає поля: menu_open")
error_case(9, "порожній підпис", lambda s: dict(copy.deepcopy(s), menu_close=" "), "Порожній підпис: menu_close")


# ======================================================================= Задача 10. Скрипт форми
FORM_ELEMENTS = [
    {"id": "contact-form", "tag": "form"},
    {"id": "f-name", "tag": "input", "value": ""},
    {"id": "f-email", "tag": "input", "value": ""},
    {"id": "form-message", "tag": "p"},
    {"id": "guest-list", "tag": "ul"},
]
FORM_HEAD = """const form = env.$("contact-form"), nm = env.$("f-name"), em = env.$("f-email"), msg = env.$("form-message"), gl = env.$("guest-list");
function send(name, email) {
  nm.value = name; em.value = email;
  const ev = env.fire(form, "submit");
  return {prevented: ev.defaultPrevented, msg: msg.textContent, error: msg.classList.contains("error"),
          alerts: env.alerts.slice(), guests: gl.children.map((c) => c.textContent), name: nm.value, email: em.value};
}
"""


def form(M, site, scenario, elements=None):
    code = out(M, 10, site)
    return run_js(code, FORM_ELEMENTS if elements is None else elements, FORM_HEAD + scenario)


def thanks(site, name):
    return site["thanks"].replace("{name}", name)


@reg(10)
def t10_success(M, site):
    r = form(M, site, 'return send("Оля", "olya@example.com");')
    assert r["prevented"] is True, "обробник має викликати event.preventDefault()"
    assert r["msg"] == thanks(site, "Оля") and r["error"] is False, f"повідомлення про успіх: {thanks(site, 'Оля')}; отримано {r['msg']!r}"
    assert r["alerts"] == [thanks(site, "Оля")], "alert має показати те саме повідомлення рівно один раз"
    assert r["guests"] == ["Оля"], "ім'я має з'явитися в списку #guest-list"
    assert r["name"] == "" and r["email"] == "", "після успіху поля очищаються"


@reg(10)
def t10_empty_name(M, site):
    r = form(M, site, 'return send("   ", "olya@example.com");')
    assert r["prevented"] is True and r["msg"] == "Вкажіть ім'я." and r["error"] is True
    assert r["alerts"] == [] and r["guests"] == [], "за помилки alert і запис у список не потрібні"


@reg(10)
def t10_bad_email(M, site):
    r = form(M, site, 'return send("Оля", "olya.example.com");')
    assert r["prevented"] is True and r["msg"] == "Перевірте адресу пошти." and r["error"] is True
    assert r["alerts"] == [] and r["guests"] == []


@reg(10)
def t10_error_then_success(M, site):
    r = form(M, site, 'send("", "a@b.cc"); return send("Іван", "a@b.cc");')
    assert r["error"] is False and r["msg"] == thanks(site, "Іван"), "після успіху клас error знімається"


error_case(10, "немає thanks", lambda s: drop(s, "thanks"), "Немає поля: thanks")
error_case(10, "шаблон без {name}", lambda s: dict(copy.deepcopy(s), thanks="Дякуємо!"), "У шаблоні немає {name}")
