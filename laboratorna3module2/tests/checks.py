"""Відкриті перевірки лабораторної роботи 3: 10 задач × 3 набори (сайти S1, S2, S3).

Кожна перевірка це функція check(mod, env): mod це модуль файла lab_NN.py, env дає сервер і тимчасову теку.
Ідентифікатор тесту: T<задача>-S<набір>-<назва>. Для однієї задачі: pytest -k T05.
"""


import copy


import csv


import io


import json


from urllib.parse import urljoin


import pytest


import requests


from bs4 import BeautifulSoup


import sites


CASES = []


def case(n, tag, open=False):
    """Реєструє перевірку задачі n для набору tag (S1, S2, S3); open=True потрапляє у відкриті тести."""
    def deco(func):
        CASES.append((n, tag, func.__name__, func, open))
        return func
    return deco


def reg(n, tag, name, func, open=False):
    """Реєструє готову перевірку під назвою name."""
    func.__name__ = name
    CASES.append((n, tag, name, func, open))


NB = "\u00a0"


CFG = sites.CONFIG


def get(site, path):
    """Текст сторінки сайту (для підготовки вхідних даних тестів)."""
    reply = requests.get(site.base + path, headers={"User-Agent": "LabTest/1.0"}, timeout=5)
    assert reply.status_code == 200, f"{path}: код {reply.status_code}"
    return reply.content.decode("utf-8")


def squash(node):
    return " ".join(node.get_text().split())


def t_fetch(url):
    """Завантажувач для тестів обходу: ValueError для будь-якого коду, окрім 200."""
    reply = requests.get(url, headers={"User-Agent": "LabTest/1.0"}, timeout=5)
    if reply.status_code != 200:
        raise ValueError(f"HTTP {reply.status_code}: {url}")
    return reply.content.decode("utf-8")


def t_parse(cfg):
    def parse(html, page_url):
        soup = BeautifulSoup(html, "html.parser")
        out = []
        for card in soup.select(cfg["item"]):
            link = card.select_one(cfg["link"])
            out.append({"title": squash(link), "url": urljoin(page_url, link["href"])})
        return out
    return parse


def t_next(cfg):
    def nxt(html, page_url):
        soup = BeautifulSoup(html, "html.parser")
        if cfg["pager"] == "rel":
            link = soup.select_one('a[rel~="next"]')
            return urljoin(page_url, link["href"]) if link else None
        if cfg["pager"] == "data":
            button = soup.select_one(cfg["pager_sel"])
            return urljoin(page_url, button["data-next"]) if button and button.get("data-next") else None
        box, seen = soup.select_one(cfg["pager_sel"]), False
        for node in box.find_all(["a", "span"]):
            classes = node.get("class", [])
            if "current" in classes:
                seen = True
            elif seen and node.name == "a" and "page" in classes:
                return urljoin(page_url, node["href"])
        return None
    return nxt


def raises(func, message, *args, **kwargs):
    with pytest.raises(ValueError) as info:
        func(*args, **kwargs)
    assert str(info.value) == message


def same(got, expected):
    assert got == expected, f"отримано {got!r}, очікувалось {expected!r}"


@case(1, "S1", open=True)
def sends_user_agent(mod, env):
    site = env.serve("S1")
    text = mod.fetch_html(site.base + "/catalog", user_agent="LabBot/2.0 (test)")
    assert "<h1>Каталог</h1>" in text
    assert site.agents == ["LabBot/2.0 (test)"]


@case(1, "S1", open=True)
def default_agent_and_block(mod, env):
    site = env.serve("S1")
    mod.fetch_html(site.base + "/catalog?page=2")
    assert site.agents[0].startswith("StudyBot/1.0")
    url = site.base + "/catalog"
    raises(mod.fetch_html, f"Доступ заборонено: {url}", url, user_agent="python-requests/2.32")


@case(1, "S1", open=True)
def not_found(mod, env):
    site = env.serve("S1")
    for path in ("/nope", "/book/99", "/catalog?page=9"):
        raises(mod.fetch_html, f"Сторінку не знайдено: {site.base + path}", site.base + path)


@case(1, "S2", open=True)
def redirect_followed(mod, env):
    site = env.serve("S2")
    text = mod.fetch_html(site.base + "/catalog")
    assert 'id="products"' in text
    assert site.paths == ["/catalog", "/shop"]


@case(1, "S2", open=True)
def server_errors(mod, env):
    site = env.serve("S2")
    for code in (500, 502, 503):
        url = f"{site.base}/status/{code}"
        raises(mod.fetch_html, f"Помилка сервера {code}: {url}", url)


@case(1, "S2", open=True)
def gone_and_other(mod, env):
    site = env.serve("S2")
    url = site.base + "/status/410"
    raises(mod.fetch_html, f"Сторінку не знайдено: {url}", url)
    url = site.base + "/status/418"
    raises(mod.fetch_html, f"Неочікуваний статус 418: {url}", url)
    url = site.base + "/status/403"
    raises(mod.fetch_html, f"Доступ заборонено: {url}", url)


@case(1, "S3", open=True)
def utf8_without_charset(mod, env):
    site = env.serve("S3")
    text = mod.fetch_html(site.base + "/jobs")
    assert "Вакансії" in text and "Python-розробник" in text and "Ð" not in text


@case(1, "S3", open=True)
def too_many_requests(mod, env):
    site = env.serve("S3")
    url = site.base + "/status/429"
    raises(mod.fetch_html, f"Забагато запитів: {url}", url)


@case(1, "S3", open=True)
def connection_refused(mod, env):
    site, stop = sites.start_site("S3")
    url = site.base + "/jobs"
    stop()
    raises(mod.fetch_html, f"Немає з'єднання: {url}", url)


BASE = "https://shop.example.org"


def robots(key):
    return sites.ROBOTS[key].format(base=BASE)


@case(2, "S1", open=True)
def s1_general_group(mod, env):
    paths = ["/", "/catalog?page=2", "/admin/", "/admin/help", "/cart", "/cartoon"]
    got = mod.robots_policy(robots("S1"), "StudyBot/1.0 (навчальний)", paths)
    same(got, {"allowed": {"/": True, "/catalog?page=2": True, "/admin/": False, "/admin/help": False,
                           "/cart": False, "/cartoon": False},
               "delay": 1.0, "sitemaps": [BASE + "/sitemap.xml"]})


@case(2, "S1", open=True)
def s1_greedy_bot(mod, env):
    got = mod.robots_policy(robots("S1"), "GreedyBot/3.1", ["/", "/catalog"])
    same(got, {"allowed": {"/": False, "/catalog": False}, "delay": None, "sitemaps": [BASE + "/sitemap.xml"]})
    same(mod.robots_policy(robots("S1"), "GREEDYBOT", ["/x"])["allowed"], {"/x": False})


@case(2, "S2", open=True)
def s2_shared_group(mod, env):
    paths = ["/cart", "/compare", "/compare/12", "/account/"]
    for agent in ("StudyBot/1.0", "ClassBot", "classbot/9"):
        got = mod.robots_policy(robots("S2"), agent, paths)
        same(got, {"allowed": {"/cart": True, "/compare": False, "/compare/12": False, "/account/": True},
                   "delay": 2.0, "sitemaps": []})


@case(2, "S2", open=True)
def s2_fallback_group(mod, env):
    got = mod.robots_policy(robots("S2"), "OtherBot/2", ["/cart", "/compare", "/account/orders", "/shop"])
    same(got, {"allowed": {"/cart": False, "/compare": False, "/account/orders": False, "/shop": True},
               "delay": 5.0, "sitemaps": []})


@case(2, "S3", open=True)
def s3_longest_match(mod, env):
    paths = ["/jobs", "/jobs/apply", "/jobs/apply/12", "/account/", "/account/orders", "/account/public",
             "/account/public/x"]
    got = mod.robots_policy(robots("S3"), "StudyBot/1.0", paths)
    same(got["allowed"], {"/jobs": True, "/jobs/apply": False, "/jobs/apply/12": False, "/account/": False,
                          "/account/orders": False, "/account/public": True, "/account/public/x": True})


@case(2, "S3", open=True)
def s3_sitemaps_no_delay(mod, env):
    got = mod.robots_policy(robots("S3"), "StudyBot/1.0", ["/"])
    same(got["delay"], None)
    same(got["sitemaps"], [BASE + "/sitemap-jobs.xml", BASE + "/sitemap-companies.xml"])


@case(2, "S3", open=True)
def empty_and_comments(mod, env):
    same(mod.robots_policy("", "Bot", ["/a"]), {"allowed": {"/a": True}, "delay": None, "sitemaps": []})
    text = "# лише коментар\n\nUSER-AGENT: *   # усі\nDISALLOW: /x # закрито\nDisallow:\n"
    same(mod.robots_policy(text, "Bot", ["/x/1", "/y"])["allowed"], {"/x/1": False, "/y": True})


def rec(title, href, price):
    return {"title": title, "href": href, "price_text": price}


S1_P1 = [rec("Кобзар", "/book/1", "249,00 грн"), rec("Лісова пісня", "/book/2", "189,50 грн"),
         rec("Захар Беркут", "/book/3", "205,00 грн"), rec("Тіні забутих предків", "/book/4", "150,00 грн"),
         rec("Енциклопедія українознавства", "/book/5", "1 249,00 грн")]


S1_P2 = [rec("Intermezzo", "/book/6", None), rec("Тигролови", "/book/7", "275,00 грн"),
         rec("Маруся Чурай", "/book/8", "199,90 грн"), rec("Чорна рада", "/book/9", "230,00 грн"),
         rec("Fata morgana", "/book/10", "120,00 грн")]


S2_P1 = [rec("Смартфон Nova X1", "/item/E-1001", "12 499 ₴"), rec("Навушники Aero Pro 2", "/item/E-1002", "3 299 ₴"),
         rec("Ноутбук Lynx 14", "/item/E-1003", "28 999 ₴"), rec("Планшет Tab Mini", "/item/E-1004", "7 999 ₴"),
         rec("Павербанк 20000 мА·год", "/item/E-1005", "899 ₴"),
         rec("Розумний годинник Pulse", "/item/E-1006", "Ціну уточнюйте")]


S2_P2 = [rec('Монітор 27" QHD', "/item/E-1007", "9 450 ₴"), rec("Клавіатура механічна K87", "/item/E-1008", "2 150 ₴"),
         rec("Миша бездротова M3", "/item/E-1009", "649 ₴"), rec("Зарядний пристрій 65 Вт", "/item/E-1010", "1 199 ₴"),
         rec("Веб-камера HD", "/item/E-1011", "1 350 ₴"), rec("Роутер Wi-Fi 6 & Mesh", "/item/E-1012", "2 799 ₴")]


S2_P3 = [rec("Кабель USB-C 1 м", "/item/E-1013", "149 ₴")]


S3_P1 = [rec("Python-розробник", "/jobs/101", "від 25 000 до 40 000 грн"),
         rec("Тестувальник QA", "/jobs/102", "від 18 000 грн"), rec("Аналітик даних", "/jobs/103", "до 45 000 грн"),
         rec("Системний адміністратор", "/jobs/104", "30 000 грн"),
         rec("Фронтенд-розробник", "/jobs/105", "за домовленістю")]


S3_P2 = [rec("DevOps-інженер", "/jobs/106", "від 55 000 до 80 000 грн"), rec("Менеджер проєктів", "/jobs/107", None),
         rec("Дизайнер інтерфейсів", "/jobs/108", "від 22 000 до 32 000 грн"),
         rec("Технічний письменник", "/jobs/109", "від 20 000 грн"), rec("Junior Python", "/jobs/110", "12 000 грн")]


S3_P3 = [rec("Адміністратор баз даних", "/jobs/111", "від 35 000 до 50 000 грн"),
         rec("Оператор підтримки", "/jobs/112", "до 16 000 грн")]


def listing_check(key, path, expected):
    def check(mod, env):
        site = env.serve(key)
        html = get(site, path)
        same(mod.parse_listing(html, CFG[key]), expected)
    return check


reg(3, "S1", "page_1", listing_check("S1", "/catalog", S1_P1), open=True)


reg(3, "S1", "page_2", listing_check("S1", "/catalog?page=2", S1_P2), open=True)


reg(3, "S2", "page_1", listing_check("S2", "/shop", S2_P1), open=True)


reg(3, "S2", "page_3", listing_check("S2", "/shop?p=3", S2_P3), open=True)


reg(3, "S3", "page_1", listing_check("S3", "/jobs", S3_P1), open=True)


reg(3, "S3", "page_2", listing_check("S3", "/jobs?offset=5", S3_P2), open=True)


def price_check(kind, pairs):
    def check(mod, env):
        for text, expected in pairs:
            got = mod.clean_price(text, kind)
            assert got == expected and type(got) is type(expected), f"{text!r}: отримано {got!r}, очікувалось {expected!r}"
    return check


reg(4, "S1", "book_prices", price_check("uah", [("249,00 грн", 249.0), ("189,50 грн", 189.5), ("199,90 грн", 199.9),
                                       ("1" + NB + "249,00" + NB + "грн", 1249.0), ("1 249,00 грн", 1249.0)]), open=True)


reg(4, "S1", "spaces_and_empty", price_check("uah", [("  120,00   грн ", 120.0), ("1\u202f249,00 грн", 1249.0),
                                            ("", None), (None, None), ("Немає в наявності", None), ("99,5 грн", 99.5)]), open=True)


reg(4, "S2", "hryvnia_sign", price_check("uah", [("12 499 ₴", 12499.0), ("899 ₴", 899.0), ("149₴", 149.0),
                                        ("28" + NB + "999" + NB + "₴", 28999.0)]), open=True)


reg(4, "S2", "unknown_and_prefix", price_check("uah", [("Ціну уточнюйте", None), ("від 999 ₴", 999.0), ("UAH 15.50", 15.5),
                                              ("2 150,5 ₴", 2150.5), ("ВІД 1 200 ГРН", 1200.0)]), open=True)


reg(4, "S3", "salary_ranges", price_check("range", [
    ("від 25 000 до 40 000 грн", {"min": 25000, "max": 40000}), ("від 18 000 грн", {"min": 18000, "max": None}),
    ("до 45 000 грн", {"min": None, "max": 45000}), ("30 000 грн", {"min": 30000, "max": 30000}),
    ("за домовленістю", {"min": None, "max": None})]), open=True)


reg(4, "S3", "salary_spaces", price_check("range", [
    ("від 55" + NB + "000 до 80" + NB + "000 грн", {"min": 55000, "max": 80000}), (None, {"min": None, "max": None}),
    ("", {"min": None, "max": None}), ("12 000 грн", {"min": 12000, "max": 12000}),
    ("  ВІД 20000  грн ", {"min": 20000, "max": None})]), open=True)


def next_check(key, path, expected_path):
    def check(mod, env):
        site = env.serve(key)
        html = get(site, path)
        expected = site.base + expected_path if expected_path else None
        same(mod.next_page_url(html, site.base + path, CFG[key]), expected)
    return check


reg(5, "S1", "first_page", next_check("S1", "/catalog", "/catalog?page=2"), open=True)


reg(5, "S1", "middle_page", next_check("S1", "/catalog?page=2", "/catalog?page=3"), open=True)


reg(5, "S1", "last_page", next_check("S1", "/catalog?page=3", None), open=True)


reg(5, "S2", "first_page", next_check("S2", "/shop", "/shop?p=2"), open=True)


reg(5, "S2", "middle_page", next_check("S2", "/shop?p=2", "/shop?p=3"), open=True)


reg(5, "S2", "last_page", next_check("S2", "/shop?p=3", None), open=True)


reg(5, "S3", "first_page", next_check("S3", "/jobs", "/jobs?offset=5"), open=True)


reg(5, "S3", "second_page", next_check("S3", "/jobs?offset=5", "/jobs?offset=10"), open=True)


reg(5, "S3", "last_page", next_check("S3", "/jobs?offset=10", None), open=True)


S1_TITLES = ["Кобзар", "Лісова пісня", "Захар Беркут", "Тіні забутих предків", "Енциклопедія українознавства",
             "Intermezzo", "Тигролови", "Маруся Чурай", "Чорна рада", "Fata morgana", "Камінний хрест",
             "Мина Мазайло", "Перехресні стежки", "Земля"]


S2_TITLES = [r["title"] for r in S2_P1 + S2_P2 + S2_P3]


S3_TITLES = [r["title"] for r in S3_P1 + S3_P2 + S3_P3]


def crawl(mod, site, **kwargs):
    cfg = site.cfg
    sleeps = []
    result = mod.crawl_listing(t_fetch, site.base + cfg["list_path"], t_parse(cfg), t_next(cfg),
                               sleep=sleeps.append, **kwargs)
    return result, sleeps


@case(6, "S1", open=True)
def full_crawl(mod, env):
    site = env.serve("S1")
    result, sleeps = crawl(mod, site, delay=1.0)
    same([r["title"] for r in result["records"]], S1_TITLES)
    same(result["pages"], [site.base + "/catalog", site.base + "/catalog?page=2", site.base + "/catalog?page=3"])
    same((result["duplicates"], result["stopped"], result["error"]), (0, "end", None))
    same(sleeps, [1.0, 1.0])
    same(site.paths, ["/catalog", "/catalog?page=2", "/catalog?page=3"])


@case(6, "S1", open=True)
def page_limit(mod, env):
    site = env.serve("S1")
    result, sleeps = crawl(mod, site, delay=0.5, max_pages=2)
    same(len(result["records"]), 10)
    same((len(result["pages"]), result["stopped"]), (2, "limit"))
    same(sleeps, [0.5])
    same(len(site.paths), 2)


@case(6, "S1", open=True)
def duplicates_removed(mod, env):
    site = env.serve("S1", dup=True)
    result, sleeps = crawl(mod, site)
    same([r["title"] for r in result["records"]], S1_TITLES)
    same((result["duplicates"], result["stopped"]), (2, "end"))


@case(6, "S2", open=True)
def s2_full_crawl(mod, env):
    site = env.serve("S2")
    result, sleeps = crawl(mod, site, delay=2.0)
    same([r["title"] for r in result["records"]], S2_TITLES)
    same(result["pages"], [site.base + "/shop", site.base + "/shop?p=2", site.base + "/shop?p=3"])
    same(sleeps, [2.0, 2.0])
    same(result["stopped"], "end")


@case(6, "S2", open=True)
def error_on_later_page(mod, env):
    site = env.serve("S2", fail_page=3)
    result, sleeps = crawl(mod, site, delay=2.0)
    same([r["title"] for r in result["records"]], S2_TITLES[:12])
    same(len(result["pages"]), 2)
    same((result["stopped"], result["error"]), ("error", f"HTTP 503: {site.base}/shop?p=3"))
    same(sleeps, [2.0, 2.0])


@case(6, "S2", open=True)
def error_on_first_page(mod, env):
    site = env.serve("S2", fail_page=1)
    raises(mod.crawl_listing, f"HTTP 503: {site.base}/shop", t_fetch, site.base + "/shop", t_parse(site.cfg),
           t_next(site.cfg), sleep=lambda s: None)


@case(6, "S3", open=True)
def cycle_stops(mod, env):
    site = env.serve("S3", loop=True)
    result, sleeps = crawl(mod, site, delay=1.0)
    same(result["pages"], [site.base + "/jobs", site.base + "/jobs?offset=5", site.base + "/jobs?offset=10",
                           site.base + "/jobs?offset=0"])
    same((result["stopped"], len(result["records"]), result["duplicates"]), ("cycle", 12, 5))
    same(sleeps, [1.0, 1.0, 1.0])
    same(len(site.paths), 4)


@case(6, "S3", open=True)
def s3_normal(mod, env):
    site = env.serve("S3")
    result, sleeps = crawl(mod, site)
    same([r["title"] for r in result["records"]], S3_TITLES)
    same((result["stopped"], result["duplicates"]), ("end", 0))


def detail_check(key, path, expected):
    def check(mod, env):
        site = env.serve(key)
        same(mod.parse_detail(get(site, path), CFG[key]), expected)
    return check


reg(7, "S1", "regular_book", detail_check("S1", "/book/1", {"title": "Кобзар", "specs": {
    "ISBN": "978-966-00-0001-1", "Сторінок": "320", "Видавець": "Основа", "Мова": "Українська"}}), open=True)


reg(7, "S1", "dash_skipped", detail_check("S1", "/book/6", {"title": "Intermezzo", "specs": {
    "Сторінок": "64", "Видавець": "Дніпро", "Мова": "Українська"}}), open=True)


reg(7, "S2", "table_rows", detail_check("S2", "/item/E-1001", {"title": "Смартфон Nova X1", "specs": {
    "Бренд": "Nova", "Гарантія": "24 міс.", "Вага": "0,18 кг"}}), open=True)


reg(7, "S2", "empty_cell_skipped", detail_check("S2", "/item/E-1006", {"title": "Розумний годинник Pulse", "specs": {
    "Бренд": "Pulse", "Вага": "0,04 кг"}}), open=True)


reg(7, "S3", "facts_list", detail_check("S3", "/jobs/101", {"title": "Python-розробник", "specs": {
    "Формат": "Віддалено", "Місто": "Львів", "Досвід": "від 2 років"}}), open=True)


reg(7, "S3", "no_experience", detail_check("S3", "/jobs/110", {"title": "Junior Python", "specs": {
    "Формат": "Офіс", "Місто": "Львів", "Досвід": "без досвіду"}}), open=True)


LISTING = [{"title": "Б", "url": "u2", "price": 150.0}, {"title": "а", "url": "u1", "price": 99.0},
           {"title": "Б", "url": "u2", "price": 150.0}, {"title": "В", "url": "u3", "price": None},
           {"title": "Intermezzo", "url": "u4", "price": 120.0}]


DETAILS = {"u1": {"ISBN": "1", "title": "X"}, "u2": {"Мова": "Укр"}, "u4": {}}


@case(8, "S1", open=True)
def sort_by_title(mod, env):
    listing, details = copy.deepcopy(LISTING), copy.deepcopy(DETAILS)
    got = mod.merge_records(listing, details)
    same([r["url"] for r in got["records"]], ["u4", "u1", "u2", "u3"])
    same(got["records"][1], {"title": "а", "url": "u1", "price": 99.0, "ISBN": "1"})
    same(got["records"][2], {"title": "Б", "url": "u2", "price": 150.0, "Мова": "Укр"})
    same((got["duplicates"], got["no_details"]), (1, ["u3"]))
    assert listing == LISTING and details == DETAILS, "вхідні дані змінено"


@case(8, "S1", open=True)
def books_by_title_code_points(mod, env):
    listing = [{"title": b[1], "url": f"/book/{b[0]}", "price": b[3]} for b in sites.BOOKS]
    got = mod.merge_records(listing, {}, sort_by="title")
    ids = [int(r["url"].rsplit("/", 1)[1]) for r in got["records"]]
    same(ids, [10, 6, 5, 3, 14, 11, 1, 2, 8, 12, 13, 7, 4, 9])
    same(len(got["no_details"]), 14)


@case(8, "S2", open=True)
def gadgets_by_price(mod, env):
    listing = [{"title": g[1], "url": f"/item/{g[0]}", "price": None if g[2] is None else float(g[2])} for g in sites.GADGETS]
    details = {f"/item/{g[0]}": {"Бренд": g[4], "Гарантія": g[5]} for g in sites.GADGETS if g[5]}
    got = mod.merge_records(listing, details, sort_by="price")
    same([r["url"][-4:] for r in got["records"]],
         ["1013", "1009", "1005", "1010", "1011", "1008", "1012", "1002", "1004", "1007", "1001", "1003", "1006"])
    same(got["records"][0], {"title": "Кабель USB-C 1 м", "url": "/item/E-1013", "price": 149.0, "Бренд": "Volt", "Гарантія": "6 міс."})
    same(got["no_details"], ["/item/E-1006"])
    same(got["records"][-1], {"title": "Розумний годинник Pulse", "url": "/item/E-1006", "price": None})


@case(8, "S2", open=True)
def keep_order_without_sort(mod, env):
    got = mod.merge_records(copy.deepcopy(LISTING), copy.deepcopy(DETAILS), sort_by=None)
    same([r["url"] for r in got["records"]], ["u2", "u1", "u3", "u4"])


@case(8, "S3", open=True)
def jobs_by_min_stable(mod, env):
    clean = {101: (25000, 40000), 102: (18000, None), 103: (None, 45000), 104: (30000, 30000), 105: (None, None),
             106: (55000, 80000), 107: (None, None), 108: (22000, 32000), 109: (20000, None), 110: (12000, 12000),
             111: (35000, 50000), 112: (None, 16000)}
    listing = [{"title": j[1], "url": f"/jobs/{j[0]}", "min": clean[j[0]][0], "max": clean[j[0]][1]} for j in sites.JOBS]
    details = {f"/jobs/{j[0]}": {"Формат": j[4], "Місто": j[5]} for j in sites.JOBS if j[0] % 2 == 1}
    got = mod.merge_records(listing, details, sort_by="min")
    same([int(r["url"].rsplit("/", 1)[1]) for r in got["records"]],
         [110, 102, 109, 108, 101, 104, 111, 106, 103, 105, 107, 112])
    same(got["records"][4], {"title": "Python-розробник", "url": "/jobs/101", "min": 25000, "max": 40000,
                             "Формат": "Віддалено", "Місто": "Львів"})
    same(got["no_details"], ["/jobs/102", "/jobs/104", "/jobs/106", "/jobs/108", "/jobs/110", "/jobs/112"])


BOM = "\ufeff"


def read_csv(path):
    raw = open(path, "rb").read()
    assert raw.startswith(b"\xef\xbb\xbf"), "CSV має починатися з BOM (utf-8-sig)"
    return raw.decode("utf-8-sig")


@case(9, "S1", open=True)
def simple_files(mod, env):
    records = [{"title": "Кобзар", "url": "u1", "price": 249.0}, {"title": "Лісова пісня", "url": "u2", "price": 189.5}]
    folder = env.tmp / "out" / "books"
    got = mod.save_dataset(records, folder, "books", ["title", "url", "price"])
    same(got, {"csv": str(folder / "books.csv"), "json": str(folder / "books.json"), "rows": 2})
    same(read_csv(got["csv"]), "title,url,price\nКобзар,u1,249.0\nЛісова пісня,u2,189.5\n")
    expected = ('[\n  {\n    "title": "Кобзар",\n    "url": "u1",\n    "price": 249.0\n  },\n  {\n    "title": "Лісова пісня",\n'
                '    "url": "u2",\n    "price": 189.5\n  }\n]\n')
    same(open(got["json"], encoding="utf-8").read(), expected)
    same(sorted(p.name for p in folder.iterdir()), ["books.csv", "books.json"])


@case(9, "S1", open=True)
def validation_errors(mod, env):
    rows = [{"a": 1}]
    folder = env.tmp / "never"
    raises(mod.save_dataset, "Немає даних для збереження", [], folder, "d", ["a"])
    raises(mod.save_dataset, "Порожній список полів", rows, folder, "d", [])
    raises(mod.save_dataset, "Повторюване поле: a", rows, folder, "d", ["a", "b", "a"])
    for name in ("", "a/b", "..\\x", ".hidden"):
        raises(mod.save_dataset, f"Некоректне ім'я файлу: {name}", rows, folder, name, ["a"])
    assert not folder.exists(), "тека не повинна створюватись, якщо дані не пройшли перевірку"


@case(9, "S2", open=True)
def quoting_and_missing(mod, env):
    records = [{"title": 'Монітор 27", QHD', "price": 9450.0, "note": "рядок 1\nрядок 2", "extra": "не зберігати"},
               {"title": "Кабель", "price": None}]
    got = mod.save_dataset(records, env.tmp, "g", ["title", "price", "note"])
    same(read_csv(got["csv"]), 'title,price,note\n"Монітор 27"", QHD",9450.0,"рядок 1\nрядок 2"\nКабель,,\n')
    same(json.loads(open(got["json"], encoding="utf-8").read()), [
        {"title": 'Монітор 27", QHD', "price": 9450.0, "note": "рядок 1\nрядок 2"},
        {"title": "Кабель", "price": None, "note": None}])
    rows = list(csv.reader(io.StringIO(read_csv(got["csv"]))))
    same(rows[1], ['Монітор 27", QHD', "9450.0", "рядок 1\nрядок 2"])


@case(9, "S2", open=True)
def json_text_format(mod, env):
    got = mod.save_dataset([{"t": "Їжак", "n": 1}], env.tmp, "u", ["t", "n"])
    raw = open(got["json"], "rb").read().decode("utf-8")
    same(raw, '[\n  {\n    "t": "Їжак",\n    "n": 1\n  }\n]\n')
    assert "\\u" not in raw and not raw.startswith(BOM)


@case(9, "S3", open=True)
def value_types(mod, env):
    records = [{"title": "Python", "remote": True, "tags": ["python", "sql"], "min": 25000, "max": None},
               {"title": "QA", "remote": False, "tags": [], "min": 18000, "max": 0.5}]
    got = mod.save_dataset(records, env.tmp, "jobs", ["title", "remote", "tags", "min", "max"])
    same(read_csv(got["csv"]), "title,remote,tags,min,max\nPython,true,python; sql,25000,\nQA,false,,18000,0.5\n")
    same(json.loads(open(got["json"], encoding="utf-8").read()), [
        {"title": "Python", "remote": True, "tags": ["python", "sql"], "min": 25000, "max": None},
        {"title": "QA", "remote": False, "tags": [], "min": 18000, "max": 0.5}])


@case(9, "S3", open=True)
def field_order_follows_fields(mod, env):
    got = mod.save_dataset([{"a": 1, "b": 2, "c": 3}], env.tmp, "o", ["c", "a"])
    same(read_csv(got["csv"]), "c,a\n3,1\n")
    same(list(json.loads(open(got["json"], encoding="utf-8").read())[0]), ["c", "a"])


def pipeline(mod, site, env, **kwargs):
    sleeps = []
    out = env.tmp / "out"
    report = mod.run_pipeline(site.base, site.cfg, out, sleep=sleeps.append, **kwargs)
    return report, sleeps, out


def read_rows(out):
    raw = (out / "dataset.csv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    return raw.decode("utf-8-sig")


@case(10, "S1", open=True)
def s1_end_to_end(mod, env):
    site = env.serve("S1")
    report, sleeps, out = pipeline(mod, site, env)
    same((report["pages"], report["items"], report["delay"], report["stopped"], report["errors"], report["rows"]),
         (3, 14, 1.0, "end", [], 14))
    same(report["files"], {"csv": str(out / "dataset.csv"), "json": str(out / "dataset.json")})
    same(sleeps, [1.0, 1.0])
    same(site.paths, ["/catalog", "/catalog?page=2", "/catalog?page=3"])
    assert all(a.startswith("StudyBot/1.0") for a in site.agents)
    lines = read_rows(out).split("\n")
    same(lines[0], "title,url,price")
    same(lines[1], f"Кобзар,{site.base}/book/1,249.0")
    same(lines[5], f"Енциклопедія українознавства,{site.base}/book/5,1249.0")
    same(lines[6], f"Intermezzo,{site.base}/book/6,")
    same(lines[7], f"Тигролови,{site.base}/book/7,275.0")
    same(len(lines), 16)
    data = json.loads((out / "dataset.json").read_text(encoding="utf-8"))
    same(data[0], {"title": "Кобзар", "url": site.base + "/book/1", "price": 249.0})
    same(data[5], {"title": "Intermezzo", "url": site.base + "/book/6", "price": None})


@case(10, "S1", open=True)
def s1_failed_page_keeps_partial(mod, env):
    site = env.serve("S1", fail_page=3)
    report, sleeps, out = pipeline(mod, site, env)
    same((report["pages"], report["items"], report["stopped"], report["errors"]),
         (2, 10, "error", [site.base + "/catalog?page=3"]))
    same(sleeps, [1.0, 1.0])
    same(len(json.loads((out / "dataset.json").read_text(encoding="utf-8"))), 10)


@case(10, "S2", open=True)
def s2_crawl_delay_from_robots(mod, env):
    site = env.serve("S2")
    report, sleeps, out = pipeline(mod, site, env)
    same((report["pages"], report["items"], report["delay"], report["stopped"]), (3, 13, 2.0, "end"))
    same(sleeps, [2.0, 2.0])
    same(site.paths, ["/shop", "/shop?p=2", "/shop?p=3"])
    lines = read_rows(out).split("\n")
    same(lines[0], "title,url,price")
    same(lines[1], f"Смартфон Nova X1,{site.base}/item/E-1001,12499.0")
    same(lines[6], f"Розумний годинник Pulse,{site.base}/item/E-1006,")
    same(lines[7], f'"Монітор 27"" QHD",{site.base}/item/E-1007,9450.0')
    same(lines[12], f"Роутер Wi-Fi 6 & Mesh,{site.base}/item/E-1012,2799.0")


@case(10, "S2", open=True)
def s2_robots_stops_at_page(mod, env):
    site = env.serve("S2", robots="User-agent: *\nDisallow: /shop?p=3\n")
    report, sleeps, out = pipeline(mod, site, env)
    same((report["pages"], report["items"], report["stopped"], report["delay"]), (2, 12, "robots", 1.0))
    same(site.paths, ["/shop", "/shop?p=2"])
    same(sleeps, [1.0])


@case(10, "S3", open=True)
def s3_range_fields(mod, env):
    site = env.serve("S3")
    report, sleeps, out = pipeline(mod, site, env)
    same((report["pages"], report["items"], report["delay"], report["stopped"]), (3, 12, 1.0, "end"))
    same(sleeps, [1.0, 1.0])
    lines = read_rows(out).split("\n")
    same(lines[0], "title,url,min,max")
    same(lines[1], f"Python-розробник,{site.base}/jobs/101,25000,40000")
    same(lines[3], f"Аналітик даних,{site.base}/jobs/103,,45000")
    same(lines[5], f"Фронтенд-розробник,{site.base}/jobs/105,,")
    same(lines[10], f"Junior Python,{site.base}/jobs/110,12000,12000")
    data = json.loads((out / "dataset.json").read_text(encoding="utf-8"))
    same(data[6], {"title": "Менеджер проєктів", "url": site.base + "/jobs/107", "min": None, "max": None})


@case(10, "S3", open=True)
def s3_cycle_and_missing_robots(mod, env):
    site = env.serve("S3", loop=True, robots=None)
    report, sleeps, out = pipeline(mod, site, env)
    same((report["pages"], report["items"], report["stopped"], report["delay"]), (4, 12, "cycle", 1.0))
    same(sleeps, [1.0, 1.0, 1.0])
    same(len(site.paths), 4)
