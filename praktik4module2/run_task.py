"""Запуск вашої задачі на навчальному сервері й збереження файлу результатів.

Використання:  python run_task.py <номер варіанта 1..30>
Скрипт піднімає локальний сервер, викликає функцію з variants/variant_NN.py на даних вашого набору
і записує результат у results/result_NN.json. Цей файл здають разом зі скриптом.
Якщо функція кидає виняток, він записується в результат як {"exception": ..., "message": ...}.
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "server"))

from open_api import Api  # noqa: E402

ADMIN, READER = "admin-token", "student-token"
HTML = "<html>Сервіс на обслуговуванні</html>"


def load_module(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ids(items):
    return [item["id"] for item in items]


def free_url():
    import socket

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return f"http://127.0.0.1:{sock.getsockname()[1]}"


def run_scenario(task, data_set, api, m, work):
    """Повертає результат сценарію (task, data_set) як значення, яке можна записати в JSON."""
    url = api.url
    if task == 1:
        return m.get_item(url, ("books", "stations", "routes")[data_set - 1], (3, 11, 99)[data_set - 1])
    if task == 2:
        if data_set == 1:
            r = m.search_items(url, "books", {"author": "Леся Українка"})
        elif data_set == 2:
            r = m.search_items(url, "stations", {"status": "на обслуговуванні"}, "altitude", True, 2)
        else:
            r = m.search_items(url, "routes", {"q": "К-10"}, "fare", True, 2)
        return {"count": r["count"], "ids": ids(r["items"]), "queries": [e["query"] for e in api.log]}
    if task == 3:
        args = {1: ("books", 5, None), 2: ("stations", 4, 2), 3: ("routes", 3, None)}[data_set]
        items = m.collect_all(url, args[0], args[1], args[2])
        return {"ids": ids(items), "requests": len(api.log)}
    if task == 4:
        name, item_id = {1: ("books", 3), 2: ("stations", 11), 3: ("routes", 7)}[data_set]
        cache, steps = {}, []
        steps.append(m.conditional_get(url, name, item_id, cache)[1])
        steps.append(m.conditional_get(url, name, item_id, cache)[1])
        api.bump(name, item_id)
        steps.append(m.conditional_get(url, name, item_id, cache)[1])
        return {"sources": steps, "etag": cache[item_id]["etag"],
                "if_none_match": [e["headers"].get("if-none-match") for e in api.log]}
    if task == 5:
        args = {1: ("books", 3, "reviews", "rating"), 2: ("stations", 4, "readings", "temp"),
                3: ("routes", 2, "stops", "minutes")}[data_set]
        return m.nested_stats(url, *args)
    if task == 6:
        if data_set == 1:
            return m.create_item(url, "books", {"title": "Вечір", "author": "Іван Франко", "pages": 30}, ADMIN)
        if data_set == 2:
            return m.create_item(url, "stations", {"name": "Тернопіль", "city": "Тернопіль", "altitude": 320}, ADMIN)
        return m.create_item(url, "routes", {"number": "К-105", "origin": "Київ", "destination": "Суми"}, READER)
    if task == 7:
        if data_set == 1:
            return m.probe(url, "/api/v1/books/99")
        if data_set == 2:
            api.inject(status=503)
            return m.probe(url, "/api/v1/stations")
        api.inject(delay=0.6)
        return m.probe(url, "/api/v1/routes", timeout=0.2)
    if task == 8:
        pauses = []
        if data_set == 1:
            api.inject(status=503, times=2)
            r = m.get_json_with_retry(url, "/api/v1/books/1", sleep=pauses.append)
        elif data_set == 2:
            api.inject(status=429, headers={"Retry-After": "3"})
            r = m.get_json_with_retry(url, "/api/v1/stations/11", sleep=pauses.append)
        else:
            api.inject(delay=0.6, times=2)
            r = m.get_json_with_retry(url, "/api/v1/routes/7", delay=0.1, sleep=pauses.append, timeout=0.2)
        return {"attempts": r["attempts"], "pauses": r["pauses"], "slept": pauses, "item_id": r["data"]["id"]}
    if task == 9:
        if data_set == 1:
            r = m.fetch_notes(url, "books", [1, 2, 99], READER)
        elif data_set == 2:
            api.inject(status=503, after=1, match="/api/v1/stations")
            r = m.fetch_notes(url, "stations", [4, 5, 6], READER)
        else:
            r = m.fetch_notes(url, "routes", [7, 8, 9, 10], READER)
        return {"result": r, "connections": len({e["port"] for e in api.log})}
    if task == 10:
        name, text = {1: ("books", "# книги\n1\n3\n99\n"), 2: ("stations", "11\n12\n7\n"),
                      3: ("routes", "7\n8\n")}[data_set]
        if data_set == 2:
            api.inject(status=503, after=1, match="/api/v1/stations")
        ids_file, out = Path(work) / "ids.txt", Path(work) / "report.json"
        ids_file.write_text(text, encoding="utf-8")
        summary = m.run_batch(url, name, ids_file, out)
        return {"summary": summary, "report": json.loads(out.read_text(encoding="utf-8"))}
    raise ValueError(f"Невідома задача: {task}")


def compute(number, module):
    """Результат варіанта number для модуля module (у вигляді, готовому до запису в JSON)."""
    task, data_set = (number - 1) // 3 + 1, (number - 1) % 3 + 1
    api = Api()
    try:
        with tempfile.TemporaryDirectory() as work:
            try:
                result = run_scenario(task, data_set, api, module, work)
            except Exception as exc:  # результат-помилка теж є результатом
                result = {"exception": type(exc).__name__, "message": str(exc)}
    finally:
        api.close()
    return json.loads(json.dumps(result, ensure_ascii=False))


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or not 1 <= int(sys.argv[1]) <= 30:
        print(__doc__)
        return 1
    number = int(sys.argv[1])
    task = (number - 1) // 3 + 1
    module = load_module(ROOT / "variants" / f"variant_{task:02d}.py")
    result = compute(number, module)
    out = ROOT / "results" / f"result_{number:02d}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nРезультат записано: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
