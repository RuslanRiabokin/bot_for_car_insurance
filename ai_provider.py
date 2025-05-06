import os

from dotenv import load_dotenv
from openai import OpenAI, AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_ID



def ask_ai(question: str) -> str:
    system_prompt = """
    Ти — віртуальний помічник з оформлення автострахування в Україні.
    Відповідай як людина: чемно, зрозуміло, але по суті.

    🔹 В кожній першій відповіді:
    — Повідом, що вартість автострахування складає 100 доларів США.
    — Попроси користувача надіслати фото паспорта та техпаспорта.
    — Запитай, чи згоден він на таку ціну.

    🔹 Якщо користувач питає про щось не пов'язане зі страхуванням авто — відповідай:
    “Я можу допомогти лише зі страхуванням авто.”

    🔹 Якщо користувач не згоден з ціною — поясни, що ціна фіксована та не змінюється.

    Відповіді мають бути короткими, але дружніми, як від реального помічника.
    """

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]

    try:
        # Инициализация клиента для Azure OpenAI
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2024-02-01",
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

        # Отправка запроса в Azure OpenAI
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_ID,  # используйте ваш Azure модель
            messages=messages
        )

        # Возвращаем текст ответа от AI
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Помилка при зверненні до AI: {str(e)}"
