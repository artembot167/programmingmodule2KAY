"""Задача 3. Пагінація.

Правила: student.md, розділ «Опис задач», задача 3.
Відкриті тести: pytest tests/test_variant_03.py
"""

"""Задача 3. Пагінація."""

import requests
from urllib.parse import urljoin


def collect_all(
    base_url: str,
    resource: str,
    page_size: int = 5,
    max_pages: int | None = None
) -> list:

    # Перевіряємо розмір сторінки
    if type(page_size) is not int or not 1 <= page_size <= 10:
        raise ValueError("page_size має бути від 1 до 10")

    # Перевіряємо максимальну кількість сторінок
    if max_pages is not None:
        if type(max_pages) is not int or max_pages < 1:
            raise ValueError("max_pages має бути не менше 1")

    headers = {
        "Accept": "application/json",
        "User-Agent": "pp-p05-student"
    }

    url = base_url + f"/api/v1/{resource}"
    params = {"limit": page_size}

    items = []
    pages_read = 0

    while url:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=5
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Помилка API: {response.status_code}"
            )

        data = response.json()
        items.extend(data["items"])
        pages_read += 1

        if max_pages is not None and pages_read >= max_pages:
            break

        next_page = data.get("next")

        if next_page is None:
            break

        url = urljoin(base_url + "/", next_page)

        # Параметри вже містяться в посиланні next
        params = None

    return items
