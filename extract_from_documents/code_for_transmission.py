from openai import AzureOpenAI
from extract_from_documents.tesseract import foto_from_folder
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

ocr_text = foto_from_folder()


check_passport_prompt = f"""
Ось фрагмент тексту, розпізнаного з документа:
\"\"\"
{ocr_text}
\"\"\"

Скажи лише "yes", якщо це український паспорт. Якщо ні — скажи "not".
Відповідь: тільки "yes" або "not".
"""

check_response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT_ID,
    messages=[
        {"role": "system", "content": "Ти помічник, який визначає, чи це український паспорт."},
        {"role": "user", "content": check_passport_prompt}
    ],
    temperature=0.1,
    max_tokens=10
)

is_passport = check_response.choices[0].message.content.strip().lower()


if is_passport == "yes":
    extract_data_prompt = f"""
    Ось фрагмент тексту, розпізнаного з українського паспорта:
    \"\"\"
    {ocr_text}
    \"\"\"

    Витягни:
    - Повне ім’я (ПІБ) у форматі: "Прізвище Ім’я" або "Прізвище Ім’я По батькові", якщо є
    - Дату народження у форматі: дд.мм.рррр

    Формат відповіді:
    {{
      "ПІБ": "...",
      "Дата народження": "..."
    }}
    """

    extract_response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT_ID,
        messages=[
            {"role": "system", "content": "Ти помічник, який витягує дані з OCR тексту паспорта."},
            {"role": "user", "content": extract_data_prompt}
        ],
        temperature=0.1,
        max_tokens=300
    )

    print(extract_response.choices[0].message.content)

else:
    print("Це не схоже на паспорт. Будь ласка, надішліть фото українського паспорта для обробки.")
