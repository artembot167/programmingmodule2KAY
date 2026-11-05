"""Локальні тестові сайти лабораторної роботи 3 (лише стандартна бібліотека, без інтернету).

Три вигадані сайти з різною розміткою:
  S1  книгарня «Лісовий кіт»      картки <article>, пагінація rel="next"
  S2  магазин електроніки «Вольт»  таблиця товарів, пагінація номерами сторінок
  S3  портал вакансій «Робота поруч» список <li>, кнопка «Показати ще» з data-next

Використання в коді:   with run_site("S2") as site: ...   (site.base = "http://127.0.0.1:<порт>")
Переглянути в браузері: python sites.py S1   (зупинка: Ctrl+C)
Усі дані вигадані; збіги з реальними назвами випадкові.
"""
import html
import json
import sys
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

NBSP = "\u00a0"

# ----------------------------------------------------------------------------------------------
# Дані (істина для тестів)
# ----------------------------------------------------------------------------------------------
# S1: id, назва, автор, ціна або None, стара ціна, сторінок, ISBN, видавець
BOOKS = [
    (1, "Кобзар", "Тарас Шевченко", 249.00, None, 320, "978-966-00-0001-1", "Основа"),
    (2, "Лісова пісня", "Леся Українка", 189.50, 210.00, 140, "978-966-00-0002-2", "Дніпро"),
    (3, "Захар Беркут", "Іван Франко", 205.00, None, 210, "978-966-00-0003-3", "Основа"),
    (4, "Тіні забутих предків", "Михайло Коцюбинський", 150.00, None, 96, "978-966-00-0004-4", "Дніпро"),
    (5, "Енциклопедія українознавства", "Колектив авторів", 1249.00, None, 880, "978-966-00-0005-5", "Наукова думка"),
    (6, "Intermezzo", "Михайло Коцюбинський", None, None, 64, "—", "Дніпро"),
    (7, "Тигролови", "Іван Багряний", 275.00, 320.00, 400, "978-966-00-0007-7", "Основа"),
    (8, "Маруся Чурай", "Ліна Костенко", 199.90, None, 160, "978-966-00-0008-8", "Дніпро"),
    (9, "Чорна рада", "Пантелеймон Куліш", 230.00, None, 350, "978-966-00-0009-9", "Основа"),
    (10, "Fata morgana", "Михайло Коцюбинський", 120.00, None, 88, "978-966-00-0010-0", "Дніпро"),
    (11, "Камінний хрест", "Василь Стефаник", 99.00, None, 72, "978-966-00-0011-7", "Дніпро"),
    (12, "Мина Мазайло", "Микола Куліш", 135.50, None, 120, "978-966-00-0012-4", "Основа"),
    (13, "Перехресні стежки", "Іван Франко", 188.00, None, 304, "978-966-00-0013-1", "Основа"),
    (14, "Земля", "Ольга Кобилянська", 142.00, None, 180, "978-966-00-0014-8", "Дніпро"),
]
BOOKS_PAGE = 5

# S2: артикул, назва, ціна (ціле, грн) або None, є в наявності, бренд, гарантія, вага
GADGETS = [
    ("E-1001", "Смартфон Nova X1", 12499, True, "Nova", "24 міс.", "0,18 кг"),
    ("E-1002", "Навушники Aero Pro 2", 3299, True, "Aero", "12 міс.", "0,05 кг"),
    ("E-1003", "Ноутбук Lynx 14", 28999, True, "Lynx", "24 міс.", "1,3 кг"),
    ("E-1004", "Планшет Tab Mini", 7999, True, "Nova", "12 міс.", "0,31 кг"),
    ("E-1005", "Павербанк 20000 мА·год", 899, True, "Volt", "12 міс.", "0,4 кг"),
    ("E-1006", "Розумний годинник Pulse", None, False, "Pulse", "", "0,04 кг"),
    ("E-1007", 'Монітор 27" QHD', 9450, True, "Lynx", "36 міс.", "4,2 кг"),
    ("E-1008", "Клавіатура механічна K87", 2150, True, "Keyra", "12 міс.", "0,9 кг"),
    ("E-1009", "Миша бездротова M3", 649, True, "Keyra", "12 міс.", "0,08 кг"),
    ("E-1010", "Зарядний пристрій 65 Вт", 1199, True, "Volt", "12 міс.", "0,17 кг"),
    ("E-1011", "Веб-камера HD", 1350, False, "Aero", "12 міс.", "0,12 кг"),
    ("E-1012", "Роутер Wi-Fi 6 & Mesh", 2799, True, "Link", "24 міс.", "0,35 кг"),
    ("E-1013", "Кабель USB-C 1 м", 149, True, "Volt", "6 міс.", "0,03 кг"),
]
GADGETS_PAGE = 6

# S3: id, посада, компанія, зарплата (як на сторінці) або None, формат, місто, досвід
JOBS = [
    (101, "Python-розробник", "ТехноЛіс", "від 25 000 до 40 000 грн", "Віддалено", "Львів", "від 2 років"),
    (102, "Тестувальник QA", "Дані та Ко", "від 18 000 грн", "Гібрид", "Київ", "від 1 року"),
    (103, "Аналітик даних", "Дані та Ко", "до 45 000 грн", "Офіс", "Одеса", "від 3 років"),
    (104, "Системний адміністратор", "Мережі+", "30 000 грн", "Офіс", "Харків", "від 2 років"),
    (105, "Фронтенд-розробник", "ТехноЛіс", "за домовленістю", "Віддалено", "Львів", "від 2 років"),
    (106, "DevOps-інженер", "ХмарУа", "від 55 000 до 80 000 грн", "Віддалено", "Київ", "від 4 років"),
    (107, "Менеджер проєктів", "Мережі+", None, "Гібрид", "Дніпро", "від 3 років"),
    (108, "Дизайнер інтерфейсів", "Пікселі", "від 22 000 до 32 000 грн", "Гібрид", "Львів", "від 1 року"),
    (109, "Технічний письменник", "ХмарУа", "від 20 000 грн", "Віддалено", "Київ", "без досвіду"),
    (110, "Junior Python", "ТехноЛіс", "12 000 грн", "Офіс", "Львів", "без досвіду"),
    (111, "Адміністратор баз даних", "Дані та Ко", "від 35 000 до 50 000 грн", "Гібрид", "Київ", "від 3 років"),
    (112, "Оператор підтримки", "Пікселі", "до 16 000 грн", "Офіс", "Одеса", "без досвіду"),
]
JOBS_PAGE = 5

# Налаштування селекторів для кожного сайту (ті самі словники наведено в студентському документі)
CONFIG = {
    "S1": {"key": "S1", "list_path": "/catalog", "item": "article.card", "link": "h3.title a",
           "title": "h3.title a", "price": "span.price", "pager": "rel", "pager_sel": "nav.pager",
           "detail_kind": "dl", "detail_title": "h1", "detail_item": "dl.specs", "price_kind": "uah",
           "min_delay": 1.0},
    "S2": {"key": "S2", "list_path": "/shop", "item": "table#products tbody tr[data-sku]", "link": "td.name a",
           "title": "td.name a", "price": "td.price", "pager": "numbered", "pager_sel": "div.pager",
           "detail_kind": "table", "detail_title": "h1", "detail_item": "table.specs", "price_kind": "uah",
           "min_delay": 1.0},
    "S3": {"key": "S3", "list_path": "/jobs", "item": "li.job", "link": "a.job-title",
           "title": "a.job-title", "price": "span.salary", "pager": "data", "pager_sel": "a.more",
           "detail_kind": "list", "detail_title": "h1", "detail_item": "ul.facts", "price_kind": "range",
           "min_delay": 1.0},
}

ROBOTS = {
    "S1": """# Книгарня «Лісовий кіт»
User-agent: *
Disallow: /admin/
Disallow: /cart
Crawl-delay: 1

User-agent: GreedyBot
Disallow: /

Sitemap: {base}/sitemap.xml
""",
    "S2": """# Магазин «Вольт»
User-agent: StudyBot
User-agent: ClassBot
Disallow: /compare
Crawl-delay: 2

User-agent: *
Disallow: /cart
Disallow: /compare
Disallow: /account/
Crawl-delay: 5
""",
    "S3": """# Портал вакансій
User-agent: *
Disallow: /jobs/apply
Disallow: /account/
Allow: /account/public
Disallow:
Sitemap: {base}/sitemap-jobs.xml
Sitemap: {base}/sitemap-companies.xml
""",
}


# ----------------------------------------------------------------------------------------------
# Форматування й розмітка
# ----------------------------------------------------------------------------------------------
def thousands(value):
    return f"{value:,}".replace(",", NBSP)


def fmt_uah(value):
    """249.0 -> '249,00 грн'; 1249.0 -> '1 249,00 грн' (нерозривні пробіли)."""
    whole, frac = f"{value:.2f}".split(".")
    return f"{thousands(int(whole))},{frac}{NBSP}грн"


def esc(text):
    return html.escape(text, quote=True)


def page(title, body, head_extra=""):
    return ('<!DOCTYPE html>\n<html lang="uk">\n<head>\n<meta charset="utf-8">\n'
            f"<title>{esc(title)}</title>\n{head_extra}</head>\n<body>\n{body}\n</body>\n</html>\n")


def s1_card(book):
    bid, title, author, price, old, *_ = book
    shown = esc(title)
    if bid == 3:                                   # зайві пропуски й переноси всередині посилання
        shown = "\n      Захар   Беркут\n    "
    if price is None:
        price_box = ""
        stock = '<p class="stock out-of-stock">Немає в наявності</p>'
    else:
        stock = '<p class="stock in-stock">Є в наявності</p>'
        if old:
            price_box = (f'<p class="price-box"><s class="old-price">{fmt_uah(old)}</s> '
                         f'<span class="price sale">{fmt_uah(price)}</span></p>')
        else:
            price_box = f'<p class="price-box"><span class="price">{fmt_uah(price)}</span></p>'
    return (f'<article class="card" data-id="{bid}">\n  <h3 class="title"><a href="/book/{bid}">{shown}</a></h3>\n'
            f'  <p class="author">{esc(author)}</p>\n  {price_box}\n  {stock}\n</article>')


def s1_list(n, pages, items, loop):
    nav = ['<nav class="pager">']
    if n > 1:
        nav.append(f'<a rel="prev" href="/catalog?page={n - 1}">Назад</a>')
    nav.append(f'<span class="current">Сторінка {n} з {pages}</span>')
    if n < pages:
        nav.append(f'<a rel="next" href="/catalog?page={n + 1}">Далі</a>')
    elif loop:
        nav.append('<a rel="next" href="/catalog?page=1">Далі</a>')
    nav.append("</nav>")
    head = '<link rel="next" href="/catalog?page=%d">\n' % (n + 1) if n < pages else ""
    body = ('<header><a href="/">Книгарня «Лісовий кіт»</a> | <a href="/catalog">Каталог</a></header>\n<main>\n'
            "<h1>Каталог</h1>\n" + "\n".join(items) + "\n" + "\n".join(nav) + "\n</main>")
    return page(f"Каталог, сторінка {n}", body, head)


def s1_detail(book):
    bid, title, author, price, old, pages, isbn, publisher = book
    rows = [("ISBN", isbn), ("Сторінок", str(pages)), ("Видавець", publisher), ("Мова", "Українська")]
    dl = "".join(f"<dt>{k}</dt><dd>{esc(v)}</dd>" for k, v in rows)
    if bid == 8:                                   # значення з пропусками й переносами
        dl = dl.replace("<dd>Дніпро</dd>", "<dd>\n   Дніпро \n</dd>")
    body = (f"<main>\n<h1>{esc(title)}</h1>\n<p class=\"author\">{esc(author)}</p>\n"
            f'<dl class="specs">{dl}</dl>\n<p><a href="/catalog">До каталогу</a></p>\n</main>')
    return page(title, body)


def s2_row(item):
    sku, name, price, stock, *_ = item
    price_html = f"{thousands(price)}{NBSP}₴" if price is not None else "Ціну уточнюйте"
    return (f'<tr data-sku="{sku}"><td class="name"><a href="/item/{sku}">{esc(name)}</a></td>'
            f'<td class="price">{price_html}</td><td class="stock">{"Є" if stock else "Немає"}</td></tr>')


def s2_list(n, pages, rows, loop):
    links = []
    for i in range(1, pages + 1):
        links.append(f'<span class="page current">{i}</span>' if i == n else f'<a class="page" href="?p={i}">{i}</a>')
    nav = '<div class="pager">' + (f'<a class="nav" href="?p={n - 1}">« Назад</a> ' if n > 1 else "") \
        + " ".join(links) + (f' <a class="nav" href="?p={n + 1}">Далі »</a>' if n < pages else "") + "</div>"
    ad = ('<tr class="ad"><td colspan="3"><a href="/promo">Реклама: знижки на аксесуари</a></td></tr>\n'
          if n == 1 else "")
    body = ('<header><a href="/">Магазин «Вольт»</a></header>\n<main>\n<h1>Товари</h1>\n'
            '<table id="products">\n<thead><tr><th>Назва</th><th>Ціна</th><th>Наявність</th></tr></thead>\n<tbody>\n'
            + ad + "\n".join(rows) + "\n</tbody>\n</table>\n" + nav + "\n</main>")
    return page(f"Товари, сторінка {n}", body)


def s2_detail(item):
    sku, name, price, stock, brand, warranty, weight = item
    rows = [("Бренд:", brand), ("Гарантія:", warranty), ("Вага:", weight)]
    trs = '<tr><th colspan="2">Характеристики</th></tr>' + "".join(
        f"<tr><th>{k}</th><td>{esc(v)}</td></tr>" for k, v in rows)
    body = f'<main>\n<h1>{esc(name)}</h1>\n<table class="specs">\n{trs}\n</table>\n</main>'
    return page(name, body)


def s3_li(job):
    jid, title, company, salary, *_ = job
    sal = f'<span class="salary">{esc(salary)}</span>' if salary else ""
    return (f'<li class="job" data-id="J-{jid}"><a class="job-title" href="/jobs/{jid}">{esc(title)}</a> '
            f'<span class="company">{esc(company)}</span> {sal}</li>')


def s3_list(offset, total, items, loop):
    nxt = offset + JOBS_PAGE
    more = ""
    if nxt < total:
        more = f'<a class="more" href="#" data-next="jobs?offset={nxt}">Показати ще</a>'
    elif loop:
        more = '<a class="more" href="#" data-next="jobs?offset=0">Показати ще</a>'
    body = ('<header><a href="/">Робота поруч</a></header>\n<main>\n<h1>Вакансії</h1>\n<ul id="jobs">\n'
            + "\n".join(items) + "\n</ul>\n" + more + "\n</main>")
    return page("Вакансії", body)


def s3_detail(job):
    jid, title, company, salary, fmt, city, exp = job
    facts = [("Формат", fmt), ("Місто", city), ("Досвід", exp)]
    lis = "<li>Опубліковано сьогодні</li>" + "".join(f"<li><b>{k}:</b> {esc(v)}</li>" for k, v in facts)
    body = f'<main>\n<h1>{esc(title)}</h1>\n<p class="company">{esc(company)}</p>\n<ul class="facts">{lis}</ul>\n</main>'
    return page(title, body)


# ----------------------------------------------------------------------------------------------
# Сервер
# ----------------------------------------------------------------------------------------------
class Site(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False

    def __init__(self, key, opts):
        super().__init__(("127.0.0.1", 0), Handler)
        self.key = key
        self.opts = opts
        self.log = []                # (шлях із запитом, User-Agent, час monotonic)
        self.lock = threading.Lock()
        self.counters = {}
        self.cfg = dict(CONFIG[key])
        data = {"S1": BOOKS, "S2": GADGETS, "S3": JOBS}[key]
        n = opts.get("items")
        self.data = list(data if n is None else data[:n])

    @property
    def base(self):
        return f"http://127.0.0.1:{self.server_address[1]}"

    @property
    def robots_text(self):
        custom = self.opts.get("robots", "default")
        if custom == "default":
            return ROBOTS[self.key].format(base=self.base)
        return custom

    @property
    def paths(self):
        """Шляхи всіх запитів у порядку отримання (без robots.txt)."""
        return [p for p, _, _ in self.log if p != "/robots.txt"]

    @property
    def agents(self):
        return [a for p, a, _ in self.log if p != "/robots.txt"]

    @property
    def times(self):
        return [t for p, _, t in self.log if p != "/robots.txt"]

    def handle_error(self, request, client_address):
        pass


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def reply(self, code, body="", ctype="text/html; charset=utf-8", headers=None):
        raw = body if isinstance(body, bytes) else body.encode("utf-8")
        site = self.server
        if site.opts.get("no_charset") or (site.key == "S3" and site.opts.get("no_charset") is None):
            ctype = ctype.split(";")[0]
        self.send_response_only(code)
        self.send_header("Server", "lab-site/1.0")
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def not_found(self):
        return self.reply(404, page("Не знайдено", "<h1>404</h1><p>Такої сторінки немає.</p>"))

    def do_GET(self):
        site = self.server
        parts = urlsplit(self.path)
        path, query = parts.path, parse_qs(parts.query)
        agent = self.headers.get("User-Agent", "")
        with site.lock:
            site.log.append((self.path, agent, time.monotonic()))
        if path == "/robots.txt":
            if site.opts.get("robots", "default") is None:
                return self.not_found()
            return self.reply(200, site.robots_text, "text/plain; charset=utf-8")
        if site.opts.get("ua_block", True) and agent.startswith("python-requests"):
            return self.reply(403, page("Заборонено", "<h1>403</h1><p>Анонімні клієнти не обслуговуються.</p>"))
        m = path.rstrip("/").rsplit("/", 1)
        if path.startswith("/status/"):                     # службові адреси для перевірки помилок
            code = int(m[-1]) if m[-1].isdigit() else 404
            extra = {"Retry-After": "2"} if code == 429 else None
            return self.reply(code, f"Код {code}", "text/plain; charset=utf-8", extra)
        if path == "/old":
            return self.reply(301, "", headers={"Location": site.cfg["list_path"]})
        handler = {"S1": self.s1, "S2": self.s2, "S3": self.s3}[site.key]
        return handler(path, query)

    # ---- S1
    def s1(self, path, query):
        site = self.server
        pages = max(1, -(-len(site.data) // BOOKS_PAGE))
        if path == "/catalog":
            try:
                n = int(query.get("page", ["1"])[0])
            except ValueError:
                n = 0
            if not 1 <= n <= pages:
                return self.not_found()
            if site.opts.get("fail_page") == n:
                return self.reply(500, "Внутрішня помилка", "text/plain; charset=utf-8")
            chunk = site.data[(n - 1) * BOOKS_PAGE: n * BOOKS_PAGE]
            if site.opts.get("dup") and n > 1:
                chunk = [site.data[(n - 1) * BOOKS_PAGE - 1]] + chunk
            return self.reply(200, s1_list(n, pages, [s1_card(b) for b in chunk], site.opts.get("loop")))
        if path.startswith("/book/") and path[6:].isdigit():
            book = next((b for b in site.data if b[0] == int(path[6:])), None)
            return self.reply(200, s1_detail(book)) if book else self.not_found()
        if path == "/":
            return self.reply(200, page("Книгарня", '<h1>Вітаємо!</h1><a href="/catalog">Каталог</a>'))
        return self.not_found()

    # ---- S2
    def s2(self, path, query):
        site = self.server
        pages = max(1, -(-len(site.data) // GADGETS_PAGE))
        if path == "/catalog":
            return self.reply(301, "", headers={"Location": "/shop"})
        if path == "/shop":
            try:
                n = int(query.get("p", ["1"])[0])
            except ValueError:
                n = 0
            if not 1 <= n <= pages:
                return self.not_found()
            if site.opts.get("fail_page") == n:
                return self.reply(503, "Тимчасово недоступно", "text/plain; charset=utf-8")
            chunk = site.data[(n - 1) * GADGETS_PAGE: n * GADGETS_PAGE]
            if site.opts.get("dup") and n > 1:
                chunk = [site.data[(n - 1) * GADGETS_PAGE - 1]] + chunk
            return self.reply(200, s2_list(n, pages, [s2_row(i) for i in chunk], site.opts.get("loop")))
        if path.startswith("/item/"):
            item = next((i for i in site.data if i[0] == path[6:]), None)
            return self.reply(200, s2_detail(item)) if item else self.not_found()
        if path == "/":
            return self.reply(200, page("Магазин", '<h1>Вітаємо!</h1><a href="/shop">Товари</a>'))
        return self.not_found()

    # ---- S3
    def s3(self, path, query):
        site = self.server
        if path == "/jobs":
            try:
                offset = int(query.get("offset", ["0"])[0])
            except ValueError:
                offset = -1
            if offset < 0 or offset % JOBS_PAGE or offset >= max(1, len(site.data)):
                return self.not_found()
            if site.opts.get("fail_page") == offset // JOBS_PAGE + 1:
                return self.reply(500, "Внутрішня помилка", "text/plain; charset=utf-8")
            chunk = site.data[offset: offset + JOBS_PAGE]
            if site.opts.get("dup") and offset > 0:
                chunk = [site.data[offset - 1]] + chunk
            return self.reply(200, s3_list(offset, len(site.data), [s3_li(j) for j in chunk], site.opts.get("loop")))
        if path.startswith("/jobs/") and path[6:].isdigit():
            job = next((j for j in site.data if j[0] == int(path[6:])), None)
            return self.reply(200, s3_detail(job)) if job else self.not_found()
        if path == "/":
            return self.reply(200, page("Робота поруч", '<h1>Вітаємо!</h1><a href="/jobs">Вакансії</a>'))
        return self.not_found()


@contextmanager
def run_site(key, **opts):
    """Запускає сайт ключа S1, S2 або S3 на вільному порту localhost і зупиняє по завершенні.

    Параметри (для перевірок): items=N (перші N записів), loop=True (остання сторінка веде на першу),
    dup=True (кожна наступна сторінка повторює останній запис попередньої), fail_page=N (сторінка N дає 5xx),
    robots=None (robots.txt відсутній) або текст robots.txt, ua_block=False, no_charset=True/False.
    """
    site = Site(key, opts)
    thread = threading.Thread(target=site.serve_forever, daemon=True)
    thread.start()
    try:
        yield site
    finally:
        site.shutdown()
        site.server_close()
        thread.join(timeout=2)


def start_site(key, **opts):
    """Те саме без контекстного менеджера: повертає (site, stop)."""
    cm = run_site(key, **opts)
    site = cm.__enter__()
    return site, lambda: cm.__exit__(None, None, None)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "S1"
    if which not in CONFIG:
        sys.exit("Використання: python sites.py S1|S2|S3")
    with run_site(which) as running:
        print(f"Сайт {which}: {running.base}{running.cfg['list_path']}  (зупинка: Ctrl+C)")
        print(json.dumps(running.cfg, ensure_ascii=False, indent=2))
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
