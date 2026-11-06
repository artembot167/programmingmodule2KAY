"""Будує графік вашого варіанта з даних вашого сервісу і зберігає його у results/.

Використання:  python make_chart.py <номер варіанта 1..30>
Сервіс запускається всередині процесу (TestClient), мережа не потрібна.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", message="Using `httpx`")

import matplotlib

matplotlib.use("Agg")
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent


def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit() or not 1 <= int(sys.argv[1]) <= 30:
        print(__doc__)
        return 1
    number = int(sys.argv[1])
    task, tag = (number - 1) // 3 + 1, f"S{(number - 1) % 3 + 1}"
    with (ROOT / "data" / f"task_{task:02d}.json").open(encoding="utf-8") as handle:
        data = json.load(handle)[tag]
    path = Path(os.environ.get("VARIANT_DIR", ROOT / "variants")) / f"variant_{task:02d}.py"
    spec = importlib.util.spec_from_file_location(f"variant_{task:02d}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    client = TestClient(module.create_app(data["records"], data["cfg"]))
    figure = module.chart_from_service(client, data["cfg"])
    out = ROOT / "results" / f"chart_{number:02d}.png"
    out.parent.mkdir(exist_ok=True)
    figure.savefig(out, dpi=120)
    print(f"Варіант {number}: задача {task}, набір {tag[1]}. Графік збережено: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
