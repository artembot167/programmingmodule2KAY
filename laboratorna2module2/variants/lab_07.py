"""Лабораторна PP-LAB02. Варіант 07: Авіарейси.

Реалізуйте сім функцій за карткою варіанта. Консольну обгортку main(argv) напишіть самостійно.
Стовпці CSV: flight, route, duration_min, delay_min, passengers.
"""

"""Лабораторна PP-LAB02. Варіант 07: Авіарейси."""

import csv
import io
import json
import re
from pathlib import Path

FIELDS = ["flight", "route", "duration_min", "delay_min", "passengers"]
ERRORS = {
    "flight": "Поле flight має формат AA000",
    "route": "Поле route має формат ПУНКТ-ПУНКТ",
    "duration_min": "Поле duration_min має бути цілим числом від 1 до 1500",
    "delay_min": "Поле delay_min має бути цілим числом від 0 до 1500",
    "passengers": "Поле passengers має бути цілим числом від 1 до 500",
}


def clean_record(raw: dict) -> dict | str:
    values = {key: str(raw.get(key, "") or "").strip() for key in FIELDS}

    if not re.fullmatch(r"[A-Z]{2}[0-9]{3}", values["flight"]):
        return ERRORS["flight"]

    route = values["route"]
    parts = route.split("-")
    if len(parts) != 2 or not all(part.strip() for part in parts):
        return ERRORS["route"]

    for key, minimum, maximum in [
        ("duration_min", 1, 1500),
        ("delay_min", 0, 1500),
        ("passengers", 1, 500),
    ]:
        value = values[key]
        if not re.fullmatch(r"[0-9]+", value):
            return ERRORS[key]
        number = int(value)
        if not minimum <= number <= maximum:
            return ERRORS[key]
        values[key] = number

    values["late"] = values["delay_min"] > 15
    return values


def load_csv(path: str) -> tuple[list[dict], list[str]]:
    records = []
    errors = []

    with open(path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != FIELDS:
            return [], ["Помилка: некоректний заголовок"]

        for line_number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                errors.append(f"Рядок {line_number}: некоректна кількість полів")
                continue

            result = clean_record(row)
            if isinstance(result, str):
                errors.append(f"Рядок {line_number}: {result}")
            else:
                records.append(result)

    return records, errors


def to_json_text(records: list[dict]) -> str:
    return json.dumps(
        {"records": records},
        indent=2,
        ensure_ascii=False
    )


def from_json_text(text: str) -> list[dict]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("Некоректний JSON") from None

    if not isinstance(data, dict) or "records" not in data:
        raise ValueError("Відсутній ключ records")

    if not isinstance(data["records"], list):
        raise ValueError("records має бути списком")

    records = []
    for item in data["records"]:
        if not isinstance(item, dict):
            raise ValueError("Запис має бути словником")

        result = clean_record(item)
        if isinstance(result, str):
            raise ValueError(result)

        records.append(result)

    return records


def to_csv_text(records: list[dict]) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(FIELDS + ["late"])

    for record in records:
        writer.writerow([
            record["flight"],
            record["route"],
            record["duration_min"],
            record["delay_min"],
            record["passengers"],
            "так" if record["late"] else "ні",
        ])

    return output.getvalue()


def convert(src: str, dst: str) -> str:
    source = Path(src)
    destination = Path(dst)

    if source.suffix.lower() == ".csv" and destination.suffix.lower() == ".json":
        records, errors = load_csv(src)
        destination.write_text(to_json_text(records), encoding="utf-8")
        return (
            f"Прочитано: {len(records) + len(errors)}, "
            f"записано: {len(records)}, пропущено: {len(errors)}"
        )

    if source.suffix.lower() == ".json" and destination.suffix.lower() == ".csv":
        records = from_json_text(source.read_text(encoding="utf-8"))
        destination.write_text(to_csv_text(records), encoding="utf-8")
        return (
            f"Прочитано: {len(records)}, "
            f"записано: {len(records)}, пропущено: 0"
        )

    raise ValueError("Непідтримуваний формат")


def summarize(records: list[dict]) -> dict:
    result = {}

    for record in records:
        route = record["route"]
        delay = record["delay_min"]

        if route not in result:
            result[route] = {"count": 0, "sum": 0}

        result[route]["count"] += 1
        result[route]["sum"] += delay

    for values in result.values():
        values["sum"] = round(values["sum"], 2)
        values["mean"] = round(values["sum"] / values["count"], 2)

    return result


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description="Конвертер авіарейсів")
    parser.add_argument("src", help="Вхідний файл")
    parser.add_argument("dst", help="Вихідний файл")
    args = parser.parse_args(argv)

    print(convert(args.src, args.dst))


if __name__ == "__main__":
    main()
