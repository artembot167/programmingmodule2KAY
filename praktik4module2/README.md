# Стартовий проєкт: практична робота 4

1. Відкрийте проєкт у GitHub Codespaces (Code → Codespaces → Create codespace) або локально: `python3 -m venv .venv`, `source .venv/bin/activate` (у Windows: `.venv\Scripts\activate`), `pip install -r requirements.txt`.
2. Визначте свою задачу за номером варіанта: задача = `(номер - 1) // 3 + 1`, набір = `(номер - 1) % 3 + 1`. Реалізуйте функцію у файлі `variants/variant_NN.py` за карткою та описом задачі в `student.md`.
3. Запускайте відкриті тести своєї задачі: `pytest tests/test_variant_NN.py` (NN з двома цифрами). Інтернет не потрібен: навчальний API піднімається локально для кожного тесту. Права адміністратора не потрібні.
4. Для ручних дослідів запустіть сервер в окремому терміналі: `python server/open_api.py`, а потім відкрийте `http://127.0.0.1:8000/api/v1/books` у браузері або виконайте `curl -i "http://127.0.0.1:8000/api/v1/books?limit=3"`.
5. Згенеруйте файл результатів: `python run_task.py <номер варіанта 1-30>`; він з'явиться в `results/result_NN.json`.
6. Змінюйте лише свій файл у `variants/`, файл `tests/test_my.py` і `ANSWERS.md`. Теки `server/`, `data/` і файли `tests/conftest.py`, `run_task.py` змінювати не можна.
7. Необов'язково: `python extra/real_api_demo.py` звертається до справжнього відкритого API (потрібен інтернет).
