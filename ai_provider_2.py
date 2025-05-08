from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from aiogram.fsm.context import FSMContext

from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_ID


async def ask_ai(question: str, state: FSMContext) -> str:
    system_prompt = """
    Ти — віртуальний помічник з оформлення автострахування в Україні.
    Відповідай як людина: чемно, зрозуміло, але по суті.

    🔹 В кожній першій відповіді:
    — Попроси користувача надіслати фото паспорта та техпаспорта.

    🔹 Якщо користувач питає про щось не пов'язане зі страхуванням авто — відповідай:
    “Я можу допомогти лише зі страхуванням авто.”

    Відповіді мають бути короткими, але дружніми, як від реального помічника.
    """

    # Получаем историю сообщений из состояния
    data = await state.get_data()
    history: list[ChatCompletionMessageParam] = data.get("chat_history", [])

    # Добавляем системное сообщение, если истории еще нет
    if not history:
        history.append({"role": "system", "content": system_prompt})

    # Добавляем новый вопрос от пользователя
    history.append({"role": "user", "content": question})

    try:
        # Инициализация клиента Azure OpenAI
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_KEY,
            api_version="2024-02-01",
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )

        # Запрос к AI с историей
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_ID,
            messages=history
        )

        ai_reply = response.choices[0].message.content.strip()

        # Добавляем ответ AI в историю
        history.append({"role": "assistant", "content": ai_reply})

        # Сохраняем обновлённую историю в FSMContext
        await state.update_data(chat_history=history)

        return ai_reply

    except Exception as e:
        return f"❌ Помилка при зверненні до AI: {str(e)}"
