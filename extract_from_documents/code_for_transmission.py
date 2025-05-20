from openai import AzureOpenAI
from extract_data_from_documents.tesseract import foto
from config import (
    AZURE_OPENAI_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT_ID,
)

# Настройка клиента Azure OpenAI
client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2024-02-01",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

# Получаем OCR текст
ocr_text = foto()

# Промпт к GPT
prompt = f"""
Ось фрагмент тексту, розпізнаного з українського паспорта:
\"\"\" 
{ocr_text} 
\"\"\" 

Будь ласка, витягни:
- Повне ім’я (ПІБ) у форматі: "Прізвище Ім’я" або "Прізвище Ім’я По батькові", якщо є
- Дату народження (дд.мм.рррр)

Відповідь поверни у форматі JSON з такими ключами:
"ПІБ", "Дата народження"
"""

# Отправка запроса к GPT (используем модель gpt-4 или gpt-35-turbo)
response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT_ID,
    messages=[
        {"role": "system", "content": "Ти помічник, який витягує дані з OCR тексту паспорта."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,
    max_tokens=300
)

# Печатаем результат
print(response.choices[0].message.content)
