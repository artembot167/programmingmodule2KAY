"""Практична робота 5. Задача 3. Розділи сторінки.

Правила: student.md, розділ «Опис задач», задача 3.
Відкриті тести: pytest -k T03
Попередній перегляд у браузері: python preview.py НОМЕР_ВАРІАНТА
"""


"""Практична робота 5. Задача 3. Розділи сторінки."""

from html import escape


def build_sections(site: dict) -> str:
    sections = site.get("sections")

    if not sections:
        raise ValueError("Немає розділів")

    result = []

    for section in sections:
        section_id = section["id"]
        title = section["title"]

        if not title.strip():
            raise ValueError(f"Порожній заголовок: {section_id}")

        result.append(
            f'<article id="{escape(section_id)}" class="section">'
        )
        result.append(f"<h2>{escape(title)}</h2>")

        for paragraph in section.get("paragraphs", []):
            result.append(f"<p>{escape(paragraph)}</p>")

        facts = section.get("facts", [])

        if facts:
            result.append('<ul class="facts">')

            for fact in facts:
                result.append(f"<li>{escape(fact)}</li>")

            result.append("</ul>")

        result.append("</article>")

    return "\n".join(result)
