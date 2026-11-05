"""Лабораторна PP-LAB02. Варіант 17: Публікації.

Реалізуйте сім функцій за карткою варіанта. Консольну обгортку main(argv) напишіть самостійно.
Стовпці CSV: author, topic, likes, comments, reposts.
"""


def clean_record(raw: dict) -> dict | str:
    """Перевіряє один рядок CSV (словник рядків); повертає запис із типами або текст першої помилки."""
    raise NotImplementedError  # TODO: реалізуйте за карткою


def load_csv(path: str) -> tuple[list[dict], list[str]]:
    """Читає CSV (UTF-8, DictReader); повертає (коректні записи, помилки)."""
    raise NotImplementedError  # TODO: реалізуйте за карткою


def to_json_text(records: list[dict]) -> str:
    """Повертає JSON-текст за структурою картки (indent=2, ensure_ascii=False)."""
    raise NotImplementedError  # TODO: реалізуйте за карткою


def from_json_text(text: str) -> list[dict]:
    """Відновлює записи з JSON-тексту; помилки — ValueError із текстом картки."""
    raise NotImplementedError  # TODO: реалізуйте за карткою


def to_csv_text(records: list[dict]) -> str:
    """Повертає CSV-текст із заголовком за форматом картки."""
    raise NotImplementedError  # TODO: реалізуйте за карткою


def convert(src: str, dst: str) -> str:
    """Конвертує файл CSV у JSON або JSON у CSV; повертає підсумковий рядок."""
    raise NotImplementedError  # TODO: реалізуйте за карткою


def summarize(records: list[dict]) -> dict:
    """Повертає підсумки за групами за правилами картки."""
    raise NotImplementedError  # TODO: реалізуйте за карткою


if __name__ == "__main__":
    pass  # TODO: консольна обгортка (шлях до файла з аргументів командного рядка)
