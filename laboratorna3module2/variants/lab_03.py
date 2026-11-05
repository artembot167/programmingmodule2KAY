"""Лабораторна робота 3. Задача 3: розбір сторінки каталогу.

Правила — у student.md (розділ 7, задача 3) та в картці вашого варіанта.
Відкриті тести: pytest tests/test_lab_03.py
"""

"""Лабораторна робота 3. Задача 3. Розбір каталогу."""

from bs4 import BeautifulSoup


def parse_listing(html: str, cfg: dict) -> list:
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for item in soup.select(cfg["item"]):
        link = item.select_one(cfg["link"])
        title = item.select_one(cfg["title"])

        if link is None or title is None:
            continue

        href = link.get("href")
        name = " ".join(title.get_text().split())

        if not href or not name:
            continue

        price = item.select_one(cfg["price"])
        price_text = None

        if price is not None:
            price_text = " ".join(price.get_text().split()) or None

        books.append({
            "title": name,
            "href": href,
            "price_text": price_text
        })

    return books
