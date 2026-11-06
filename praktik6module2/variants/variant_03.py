"""Задача 3. Створення записів і валідація.

Правила: student.md, розділ «Опис задач», задача 3.
Відкриті тести: pytest tests/test_variant_03.py
"""

from copy import deepcopy

import matplotlib.pyplot as plt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator


class NewRecord(BaseModel):
    name: str
    group: str
    value: float = Field(ge=0)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if not 2 <= len(value) <= 40:
            raise ValueError("Ім'я повинно містити 2-40 символів")
        return value


def create_app(records: list[dict], cfg: dict) -> FastAPI:
    app = FastAPI()
    items = deepcopy(records)
    base = "/" + cfg["resource"]

    @app.get(base)
    def get_items():
        ordered = sorted(items, key=lambda item: item["id"])
        return {"count": len(ordered), "items": ordered}

    @app.get(base + "/stats")
    def get_stats():
        counts = {
            group: sum(item["group"] == group for item in items)
            for group in cfg["groups"]
        }
        return {"total": len(items), "by_group": counts}

    @app.post(base, status_code=201)
    def add_item(record: NewRecord):
        if record.group not in cfg["groups"]:
            raise HTTPException(
                status_code=422,
                detail="Невідома група"
            )

        if record.value > cfg["max_value"]:
            raise HTTPException(
                status_code=422,
                detail="Значення завелике"
            )

        for item in items:
            if (
                item["group"] == record.group
                and item["name"].lower() == record.name.lower()
            ):
                raise HTTPException(
                    status_code=409,
                    detail="Запис уже існує"
                )

        new_id = max(
            (item["id"] for item in items),
            default=0
        ) + 1

        new_item = {
            "id": new_id,
            "name": record.name,
            "group": record.group,
            "value": float(record.value)
        }

        items.append(new_item)
        return new_item

    return app


def build_figure(payload: dict, cfg: dict):
    fig, ax = plt.subplots()
    by_group = payload["by_group"]

    labels = [
        group for group, count in by_group.items()
        if count > 0
    ]
    values = [
        count for count in by_group.values()
        if count > 0
    ]

    if values:
        ax.pie(
            values,
            labels=labels,
            autopct="%1.0f%%"
        )
    else:
        ax.text(
            0.5, 0.5, "Немає даних",
            ha="center",
            va="center",
            transform=ax.transAxes
        )
        ax.set_axis_off()

    ax.set_title(cfg["title"])
    return fig


def chart_from_service(client, cfg: dict):
    response = client.get(cfg["report_url"])
    response.raise_for_status()
    return build_figure(response.json(), cfg)
