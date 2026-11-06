"""Запускає сервіс вашого варіанта на 127.0.0.1:8000 для ручного дослідження.

Використання:  python serve.py <номер варіанта 1..30>
Документація API: http://127.0.0.1:8000/docs . Зупинка: Ctrl+C.
"""
import importlib.util
import json
import sys
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", message="Using `httpx`")

import uvicorn

ROOT = Path(__file__).resolve().parent


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or not 1 <= int(sys.argv[1]) <= 30:
        print(__doc__)
        return 1
    number = int(sys.argv[1])
    task, tag = (number - 1) // 3 + 1, f"S{(number - 1) % 3 + 1}"
    with (ROOT / "data" / f"task_{task:02d}.json").open(encoding="utf-8") as handle:
        data = json.load(handle)[tag]
    path = ROOT / "variants" / f"variant_{task:02d}.py"
    spec = importlib.util.spec_from_file_location(f"variant_{task:02d}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.create_app(data["records"], data["cfg"])
    uvicorn.run(app, host="127.0.0.1", port=8000)
    return 0


if __name__ == "__main__":
    sys.exit(main())
