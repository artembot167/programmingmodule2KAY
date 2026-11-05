"""Необов'язкове продовження: справжній відкритий API без ключа (Open-Meteo).

Запуск:  python extra/real_api_demo.py
Потрібен інтернет. Перевірка тестами не виконується: це вправа для цікавості.
Умови безкоштовного використання: https://open-meteo.com/en/pricing (некомерційне використання, ліміт запитів на добу).
"""
import json
from pathlib import Path

import requests

URL = "https://api.open-meteo.com/v1/forecast"
HEADERS = {"Accept": "application/json", "User-Agent": "pp-p05-student"}
CITIES = {"Київ": (50.45, 30.52), "Львів": (49.84, 24.03), "Одеса": (46.48, 30.73)}


def current_weather(latitude: float, longitude: float) -> dict:
    """Повертає поточну температуру й вітер для координат (параметри передаються через params=)."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,wind_speed_10m",
        "timezone": "auto",
    }
    response = requests.get(URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    body = response.json()
    return {
        "temperature": body["current"]["temperature_2m"],
        "wind": body["current"]["wind_speed_10m"],
        "units": {
            "temperature": body["current_units"]["temperature_2m"],
            "wind": body["current_units"]["wind_speed_10m"],
        },
    }


def main() -> None:
    result = {}
    for city, (lat, lon) in CITIES.items():
        try:
            result[city] = current_weather(lat, lon)
        except requests.exceptions.RequestException as exc:
            result[city] = {"error": type(exc).__name__}
        print(city, result[city])
    out = Path(__file__).resolve().parent.parent / "results" / "real_weather.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Збережено:", out.name)


if __name__ == "__main__":
    main()
