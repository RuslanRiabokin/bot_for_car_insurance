import os
from glob import glob
from google import genai
from google.genai import types
from config import GEMINI_API
import json

# Настройка API ключа
client = genai.Client(api_key=GEMINI_API)

# Путь к папке с изображениями
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
temp_dir = os.path.abspath(os.path.join(BASE_DIR, '..', 'temp'))

# Поддерживаемые расширения изображений
image_extensions = ['*.jpg', '*.jpeg', '*.png']

# Сбор всех изображений из папки temp
image_paths = []
for ext in image_extensions:
    image_paths.extend(glob(os.path.join(temp_dir, ext)))

# Проверка количества найденных файлов (ожидается от 2 до 3)
if not (2 <= len(image_paths) <= 3):
    print(f"ОШИБКА: Ожидалось от 2 до 3 изображений, найдено {len(image_paths)}:")
    for p in image_paths:
        print(f" - {p}")
    exit()

# Опционально: сортировка по имени (предполагаем, что паспорт идёт первым)
image_paths = sorted(image_paths)

# Подготовка изображений
image_parts = []
for path in image_paths:
    try:
        with open(path, 'rb') as f:
            image_parts.append(types.Part.from_bytes(data=f.read(), mime_type='image/jpeg'))
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути '{path}'")
        exit()

# Промпт на украинском языке с конкретными полями
prompt = """
Ти — асистент зі зчитування документів. Твоя задача — уважно проаналізувати 2 або 3 зображення (перше — паспорт громадянина України, друге — техпаспорт на автомобіль, третє — зворот техпаспорта, якщо є) та витягти з них такі ключові дані:

- ПІБ (повністю, з паспорта)
- Номер авто (державний номер, з техпаспорта)
- VIN (ідентифікаційний номер авто, з техпаспорта)
- Дата народження (з паспорта)

Поверни результат **тільки у вигляді JSON**, як у прикладі нижче:

{
    "ПІБ": "Бондаренко Василь Васильович",
    "Номер авто": "KE1234AE",
    "VIN": "VF1ABC1234567890",
    "Дата народження": "01.01.1990"
}

⚠️ Якщо якусь інформацію не вдалося розпізнати — залиш її значення пустим (""), але поле обов’язково має бути.

Зображення подані у наступному порядку:
1. Паспорт
2. Техпаспорт (лицева сторона)
3. Техпаспорт (зворот) — якщо є
"""

# Настройка запроса
config = types.GenerateContentConfig(response_mime_type="application/json")

# Отправка запроса
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[prompt] + image_parts,
    config=config
)

# Обработка ответа
try:
    extracted_data = json.loads(response.text)
    print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
except (json.JSONDecodeError, KeyError) as e:
    print(f"Не удалось обработать ответ от API: {e}")
    print(f"Ответ API: {response.text}")
