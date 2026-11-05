"""Збирає папку site/ для перегляду в браузері (Live Server у Codespaces або VS Code).

Використання:
    python preview.py НОМЕР_ВАРІАНТА          # зібрати site/
    python preview.py НОМЕР_ВАРІАНТА --zip   # зібрати site/ і створити submit.zip для здачі

Номер варіанта 1..30: задача = (номер - 1) // 3 + 1, набір (сайт) = (номер - 1) % 3 + 1.
Скрипт викликає функцію з вашого файла variants/variant_NN.py, кладе результат у потрібне місце сторінки,
а решту сторінки бере із site_base/. Цей файл змінювати не потрібно.
"""
import importlib.util
import json
import re
import struct
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FUNCS = {1: "build_page", 2: "build_nav", 3: "build_sections", 4: "build_price_table", 5: "build_gallery",
         6: "build_contact_form", 7: "build_base_css", 8: "build_selector_css", 9: "build_menu_script",
         10: "build_form_script"}


def png(width, height, rgb):
    """Однотонне зображення-заповнювач у форматі PNG (без сторонніх бібліотек)."""
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    row = b"\x00" + bytes(rgb) * width
    raw = zlib.compress(row * height)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


def main(argv):
    if len(argv) < 2 or not argv[1].isdigit() or not 1 <= int(argv[1]) <= 30:
        print(__doc__)
        return 1
    number = int(argv[1])
    task, theme = (number - 1) // 3 + 1, (number - 1) % 3 + 1
    sites = json.loads((ROOT / "data" / "sites.json").read_text(encoding="utf-8"))
    site = sites[theme - 1]
    path = ROOT / "variants" / f"variant_{task:02d}.py"
    spec = importlib.util.spec_from_file_location("student_variant", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        result = getattr(module, FUNCS[task])(site)
    except NotImplementedError:
        print(f"Задачу {task} ще не реалізовано: див. {path.name}")
        return 1
    if not isinstance(result, str):
        print("Функція має повертати рядок (str)")
        return 1

    out = ROOT / "site"
    (out / "img").mkdir(parents=True, exist_ok=True)
    base = ROOT / "site_base"
    page = (base / f"page_{theme}.html").read_text(encoding="utf-8")
    css = (base / "base.css").read_text(encoding="utf-8")
    js = (base / "base.js").read_text(encoding="utf-8")
    if task == 1:
        page = result
    elif task <= 6:
        page = re.sub(rf"<!--SLOT:{task}-->.*?<!--/SLOT:{task}-->", lambda m: result, page, flags=re.S)
    elif task <= 8:
        css = result
    else:
        js = result
    page = re.sub(r"<!--/?SLOT:\d+-->\n?", "", page)
    (out / "index.html").write_text(page, encoding="utf-8")
    (out / "style.css").write_text(css, encoding="utf-8")
    (out / "script.js").write_text(js, encoding="utf-8")
    palette = [(120, 160, 200), (200, 160, 120), (140, 190, 140), (190, 140, 190)]
    for k, image in enumerate(site["gallery"]):
        (out / "img" / image["file"]).write_bytes(png(image["width"] // 4, image["height"] // 4, palette[k % 4]))
    print(f"Готово: {out / 'index.html'}. Відкрийте його через Live Server (Go Live) або у браузері.")
    if "--zip" in argv:
        target = ROOT / "submit.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(path, f"variants/variant_{task:02d}.py")
            for f in sorted(out.rglob("*")):
                if f.is_file():
                    z.write(f, f"site/{f.relative_to(out).as_posix()}")
            for extra in ("ANSWERS.md", "tests/test_my.py"):
                if (ROOT / extra).exists():
                    z.write(ROOT / extra, extra)
        print(f"Архів для здачі: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
