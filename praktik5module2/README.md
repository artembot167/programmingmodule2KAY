# Стартовий проєкт: практична робота 5

1. Відкрийте проєкт у GitHub Codespaces (Code → Codespaces → Create codespace) або локально: `python3 -m venv .venv`, `source .venv/bin/activate` (у Windows: `.venv\Scripts\activate`), `pip install -r requirements.txt`. Для JS-перевірок потрібен Node.js (у Codespaces він уже встановлений).
2. Визначте свою задачу за номером варіанта: задача = `(номер - 1) // 3 + 1`, сайт = `(номер - 1) % 3 + 1`. Реалізуйте функцію у файлі `variants/variant_NN.py` за карткою.
3. Запускайте відкриті тести своєї задачі: `pytest -k T05` (замість 05 номер вашої задачі з двома цифрами).
4. Перегляд у браузері: `python preview.py НОМЕР_ВАРІАНТА`, потім відкрийте `site/index.html` через Live Server (кнопка Go Live) або у браузері.
5. Змінюйте лише свій файл у `variants/`, файл `tests/test_my.py` і `ANSWERS.md`. Дані сайтів лежать у `data/sites.json`.
6. Здача: `python preview.py НОМЕР_ВАРІАНТА --zip` створює `submit.zip`.
