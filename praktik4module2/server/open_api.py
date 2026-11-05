"""Локальний навчальний REST API для практичної роботи 4 (лише стандартна бібліотека).

Сервер працює на 127.0.0.1, не потребує ключів і інтернету. Дані беруться з файлів теки data/.
Три колекції з однаковими правилами: books (бібліотека), stations (метеостанції), routes (маршрути).

Запуск у терміналі для ручних дослідів:   python server/open_api.py   (порт 8000)
Запуск із коду / тестів:                  with run_api() as api: api.url ...

Адреси:
  GET|HEAD /api/v1                           перелік колекцій
  GET|HEAD /api/v1/<колекція>                список: page, limit (1..10), sort, order, q, фільтри за полями
  GET|HEAD /api/v1/<колекція>/<id>           один запис із вкладеними даними; ETag, If-None-Match -> 304
  GET      /api/v1/<колекція>/<id>/private   нотатка до запису; потрібен Bearer student-token або admin-token
  POST     /api/v1/<колекція>                створення запису; потрібен Bearer admin-token, тіло JSON

Для дослідів із помилками є метод api.inject(...): він ставить у чергу штучні збої (503, 429 з Retry-After,
затримку, не-JSON відповідь), які отримають наступні запити.
"""

import json
import threading
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOKENS = {"student-token": "read", "admin-token": "write"}
MAX_LIMIT = 10

# для кожної колекції: поле для пошуку q, унікальне поле, обов'язкові поля, цілі поля, вкладені списки
SCHEMA = {
    "books": {
        "label": "title",
        "unique": "title",
        "required": ["title", "author", "pages"],
        "ints": ["pages"],
        "nested": ["reviews"],
        "fields": ["id", "title", "author", "genre", "pages", "price"],
    },
    "stations": {
        "label": "name",
        "unique": "name",
        "required": ["name", "city", "altitude"],
        "ints": ["altitude"],
        "nested": ["readings"],
        "fields": ["id", "name", "city", "altitude", "temp", "humidity", "status"],
    },
    "routes": {
        "label": "number",
        "unique": "number",
        "required": ["number", "origin", "destination"],
        "ints": ["distance_km"],
        "nested": ["stops"],
        "fields": ["id", "number", "origin", "destination", "distance_km", "fare", "kind"],
    },
}


def load_data():
    return {
        name: [dict(item, rev=1) for item in json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))]
        for name in SCHEMA
    }


class State:
    """Дані сервера, журнал запитів і черга штучних збоїв."""

    def __init__(self):
        self.data = load_data()
        self.log = []
        self.faults = []
        self.lock = threading.Lock()

    def next_id(self, name):
        return max(item["id"] for item in self.data[name]) + 1


class Server(ThreadingHTTPServer):
    daemon_threads = True
    block_on_close = False

    def __init__(self, addr):
        super().__init__(addr, Handler)
        self.state = State()

    def handle_error(self, request, client_address):
        pass  # клієнт міг обірвати з'єднання (тайм-аут) - це не помилка сервера


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    # ---------- відповіді ----------
    def reply(self, code, body=None, headers=None, ctype="application/json; charset=utf-8"):
        if body is None:
            raw = b""
        elif isinstance(body, bytes):
            raw = body
        elif isinstance(body, str):
            raw = body.encode("utf-8")
        else:
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response_only(code)
        self.send_header("Server", "pp-p05-api/1.0")
        if code not in (204, 304):
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(raw)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(raw)

    def error(self, code, text, headers=None):
        self.reply(code, {"error": text}, headers)

    # ---------- допоміжне ----------
    def auth(self, need):
        value = self.headers.get("Authorization", "")
        if not value.startswith("Bearer "):
            self.error(401, "потрібна автентифікація", {"WWW-Authenticate": 'Bearer realm="pp-p05"'})
            return False
        scope = TOKENS.get(value[7:])
        if scope is None:
            self.error(401, "недійсний токен", {"WWW-Authenticate": 'Bearer realm="pp-p05", error="invalid_token"'})
            return False
        if need == "write" and scope != "write":
            self.error(403, "недостатньо прав для запису")
            return False
        return True

    def apply_fault(self, path):
        """Бере з черги перший збій, що підходить до адреси. Повертає True, якщо відповідь уже надіслано."""
        state = self.server.state
        with state.lock:
            fault = None
            for candidate in state.faults:
                if not path.startswith(candidate["match"]):
                    continue
                if candidate["after"] > 0:
                    candidate["after"] -= 1  # цей запит ще проходить без збою
                    continue
                fault = candidate
                break
            if fault is None:
                return False
            fault["times"] -= 1
            if fault["times"] <= 0:
                state.faults.remove(fault)
        if fault["delay"]:
            time.sleep(fault["delay"])
        if fault["body"] is not None:
            self.reply(fault["status"] or 200, fault["body"], fault["headers"], fault["ctype"])
            return True
        if fault["status"]:
            self.error(fault["status"], "штучний збій сервера", fault["headers"])
            return True
        return False  # лише затримка: далі звичайна обробка

    def route(self):
        state = self.server.state
        self.raw_body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        url = urlsplit(self.path)
        pairs = parse_qsl(url.query, keep_blank_values=True)
        with state.lock:
            state.log.append(
                {
                    "method": self.command,
                    "path": url.path,
                    "target": self.path,
                    "query": dict(pairs),
                    "headers": {k.lower(): v for k, v in self.headers.items()},
                    "port": self.client_address[1],
                    "body": self.raw_body.decode("utf-8", "replace"),
                }
            )
        if self.apply_fault(url.path):
            return
        parts = [p for p in url.path.split("/") if p]
        method = self.command
        if parts[:2] != ["api", "v1"]:
            return self.error(404, f"адресу {url.path} не знайдено")
        parts = parts[2:]
        if not parts:
            return self.reply(200, {"version": "1", "resources": list(SCHEMA)})
        name = parts[0]
        if name not in SCHEMA:
            return self.error(404, f"колекцію {name} не знайдено")
        if len(parts) == 1:
            if method in ("GET", "HEAD"):
                return self.list_items(name, pairs)
            if method == "POST":
                return self.create_item(name)
            return self.error(405, "метод не підтримується", {"Allow": "GET, HEAD, POST"})
        raw_id = parts[1]
        item = None
        if raw_id.isdigit():
            item = next((i for i in state.data[name] if i["id"] == int(raw_id)), None)
        if item is None:
            return self.error(404, f"запис {raw_id} не знайдено")
        if len(parts) == 2:
            if method not in ("GET", "HEAD"):
                return self.error(405, "метод не підтримується", {"Allow": "GET, HEAD"})
            return self.one_item(name, item)
        if len(parts) == 3 and parts[2] == "private" and method == "GET":
            if self.auth("read"):
                label = item[SCHEMA[name]["label"]]
                self.reply(200, {"id": item["id"], "note": f"Службова нотатка до запису «{label}»"})
            return
        return self.error(404, f"адресу {url.path} не знайдено")

    do_GET = do_HEAD = do_POST = do_PUT = do_DELETE = route

    # ---------- обробники ----------
    def flat(self, name, item):
        return {k: item[k] for k in SCHEMA[name]["fields"]}

    def list_items(self, name, pairs):
        schema = SCHEMA[name]
        state = self.server.state
        params = {}
        for key, value in pairs:
            params.setdefault(key, value)
        known = {"page", "limit", "sort", "order", "q"} | set(schema["fields"])
        for key in params:
            if key not in known:
                return self.error(400, f"невідомий параметр: {key}")
        try:
            page = int(params.get("page", 1))
            if page < 1:
                raise ValueError
        except ValueError:
            return self.error(400, "page має бути цілим числом не менше 1")
        try:
            limit = int(params.get("limit", 5))
            if not 1 <= limit <= MAX_LIMIT:
                raise ValueError
        except ValueError:
            return self.error(400, f"limit має бути цілим числом від 1 до {MAX_LIMIT}")
        sort = params.get("sort", "id")
        if sort not in schema["fields"]:
            return self.error(400, f"невідоме поле сортування: {sort}")
        order = params.get("order", "asc")
        if order not in ("asc", "desc"):
            return self.error(400, "order має бути asc або desc")
        items = [self.flat(name, i) for i in state.data[name]]
        for key in schema["fields"]:
            if key in params:
                items = [i for i in items if str(i[key]) == params[key]]
        if "q" in params:
            needle = params["q"].casefold()
            items = [i for i in items if needle in str(i[schema["label"]]).casefold()]
        items.sort(key=lambda i: i["id"])
        items.sort(key=lambda i: (i[sort] is None, 0 if i[sort] is None else i[sort]), reverse=(order == "desc"))
        total = len(items)
        chunk = items[(page - 1) * limit : page * limit]
        nxt = None
        if page * limit < total:
            rest = {k: v for k, v in params.items() if k not in ("page", "limit")}
            nxt = f"/api/v1/{name}?" + urlencode({"page": page + 1, "limit": limit, **rest})
        self.reply(
            200,
            {"count": total, "page": page, "limit": limit, "items": chunk, "next": nxt},
            {"X-Total-Count": str(total)},
        )

    def one_item(self, name, item):
        etag = f'"{item["id"]}-{item["rev"]}"'
        if self.headers.get("If-None-Match") == etag:
            return self.reply(304, None, {"ETag": etag})
        body = self.flat(name, item)
        for key in SCHEMA[name]["nested"]:
            body[key] = item[key]
        self.reply(200, body, {"ETag": etag})

    def create_item(self, name):
        if not self.auth("write"):
            return
        schema = SCHEMA[name]
        state = self.server.state
        if "application/json" not in self.headers.get("Content-Type", ""):
            return self.error(415, "очікується application/json")
        try:
            data = json.loads(self.raw_body)
        except ValueError:
            return self.error(400, "некоректний JSON")
        if not isinstance(data, dict):
            return self.error(400, "очікується JSON-об'єкт")
        for field in schema["required"]:
            if data.get(field) in (None, ""):
                return self.error(422, f"поле {field} обов'язкове")
        for field in schema["ints"]:
            if field in data and (isinstance(data[field], bool) or not isinstance(data[field], int)):
                return self.error(422, f"поле {field} має бути цілим числом")
        if name == "books" and data["pages"] <= 0:
            return self.error(422, "поле pages має бути додатним")
        with state.lock:
            if any(i[schema["unique"]] == data[schema["unique"]] for i in state.data[name]):
                return self.error(409, f"запис із таким значенням поля {schema['unique']} уже є")
            item = {"id": state.next_id(name)}
            item.update({k: data.get(k) for k in schema["fields"] if k != "id"})
            for key in schema["nested"]:
                item[key] = []
            item["rev"] = 1
            state.data[name].append(item)
        self.reply(201, self.flat(name, item), {"Location": f"/api/v1/{name}/{item['id']}"})


class Api:
    """Запущений сервер: адреса, журнал запитів, керування збоями."""

    def __init__(self):
        self.server = Server(("127.0.0.1", 0))
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
        self.thread.start()

    @property
    def log(self):
        return self.server.state.log

    @property
    def data(self):
        return self.server.state.data

    def inject(self, status=None, times=1, match="/api/v1", delay=0.0, headers=None, body=None,
               ctype="application/json; charset=utf-8", after=0):
        """Ставить у чергу times збоїв для наступних запитів, адреса яких починається з match.

        status - код відповіді (503, 429...); headers - додаткові заголовки (наприклад Retry-After);
        delay - пауза в секундах перед відповіддю; body/ctype - власне тіло відповіді (текст чи bytes).
        after - скільки підходящих запитів пропустити без збою, перш ніж він почне діяти.
        Без status і body збій лише затримує звичайну відповідь.
        """
        with self.server.state.lock:
            self.server.state.faults.append(
                {"status": status, "times": times, "match": match, "delay": delay,
                 "headers": headers or {}, "body": body, "ctype": ctype, "after": after}
            )

    def bump(self, name, item_id, **changes):
        """Змінює запис на сервері й збільшує його версію (змінюється ETag)."""
        for item in self.data[name]:
            if item["id"] == item_id:
                item.update(changes)
                item["rev"] += 1

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@contextmanager
def run_api():
    api = Api()
    try:
        yield api
    finally:
        api.close()


if __name__ == "__main__":
    server = Server(("127.0.0.1", 8000))
    print("Навчальний API працює: http://127.0.0.1:8000/api/v1  (зупинка: Ctrl+C)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
