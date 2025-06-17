import os
from glob import glob
from google import genai
from google.genai import types
from config import GEMINI_API
import json

# Настройка API ключа
client = genai.Client(api_key=GEMINI_API)

# Путь к папке с изображениями
#temp_dir = 'temp'
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

# Опционально: сортировка по имени, если важно, чтобы паспорт шёл первым
image_paths = sorted(image_paths)  # По алфавиту, можно заменить на кастомную логику

# Подготовка изображений
image_parts = []
for path in image_paths:
    try:
        with open(path, 'rb') as f:
            image_parts.append(types.Part.from_bytes(data=f.read(), mime_type='image/jpeg'))
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути '{path}'")
        exit()

# Промпт для извлечения данных
prompt = """
Ты — ассистент по обработке документов. Твоя задача — извлечь информацию из двух или трёх предоставленных изображений (паспорт, лицевая и обратная стороны техпаспорта) и вернуть результат в виде единого JSON объекта.

Первое изображение - это паспорт.
Второе - лицевая сторона техпаспорта на машину.
Третье (если есть) - обратная сторона техпаспорта.

Извлеки следующие поля и заполни их. Если какое-то поле не найдено, оставь значение пустым ("").

{
  "passport": {
    "document_type": "паспорт",
    "last_name": "",
    "first_name": "",
    "patronymic": "",
    "series_and_number": "",
    "date_of_birth": "",
    "place_of_birth": "",
    "issued_by": "",
    "date_of_issue": ""
  },
  "vehicle_registration": {
    "document_type": "техпаспорт",
    "license_plate": "",
    "vin_code": "",
    "brand_model": "",
    "category": "",
    "year_of_manufacture": "",
    "engine_volume": "",
    "color": "",
    "owner_full_name": "",
    "special_notes": ""
  }
}
"""

# Запрос с ожиданием JSON-ответа
config = types.GenerateContentConfig(response_mime_type="application/json")

# Отправка запроса

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[prompt] + image_parts,
    config=config
 )

# Обработка ответа (если запрос активен)
try:
    extracted_data = json.loads(response.text)
    print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
except (json.JSONDecodeError, KeyError) as e:
    print(f"Не удалось обработать ответ от API: {e}")
    print(f"Ответ API: {response.text}")
