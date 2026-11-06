# Стартовий проєкт: практична робота 6

1. Відкрийте проєкт у GitHub Codespaces (Code → Codespaces → Create codespace) або локально: `python3 -m venv .venv`, `source .venv/bin/activate` (у Windows: `.venv\Scripts\activate`), `pip install -r requirements.txt`.
2. Визначте свою задачу за номером варіанта: задача = `(номер - 1) // 3 + 1`, набір = `(номер - 1) % 3 + 1`. Реалізуйте задачу у файлі `variants/variant_NN.py` за правилами й карткою (три функції: `create_app`, `build_figure`, `chart_from_service`).
3. Запускайте відкриті тести своєї задачі: `pytest tests/test_variant_NN.py` (NN з двома цифрами). Права адміністратора й мережа не потрібні.
4. Для ручного дослідження сервісу: `python serve.py <номер варіанта>`, потім `http://127.0.0.1:8000/docs`.
5. Графік вашого варіанта: `python make_chart.py <номер варіанта>`; зображення з'явиться в `results/chart_<номер варіанта>.png`.
6. Змінюйте лише свій файл у `variants/`, файл `tests/test_my.py` і вміст `results/`. Дані трьох наборів кожної задачі лежать у `data/task_NN.json`.
