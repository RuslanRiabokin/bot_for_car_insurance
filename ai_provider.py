from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam
from aiogram.fsm.context import FSMContext

from config import AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_ID

async def reset_chat_history(state: FSMContext):
    await state.update_data(chat_history=[])


async def ask_ai(question: str, state: FSMContext) -> str:
    system_prompt = """
    Ти — віртуальний страховий консультант, який допомагає клієнтам оформити автострахування в Україні.
    Відповідай коротко, зрозуміло й доброзичливо — як справжній співробітник страхової компанії.

    🔹 Завжди дотримуйся такого стилю:
    — Привітний тон, прості речення, чіткі інструкції.
    — Якщо користувач ще не надіслав документи, попроси фото паспорта та техпаспорта.
    — Якщо користувач вже надіслав документи, поводься так, ніби ти їх **проаналізував**.

    🔹 Якщо дані вже витягнуті (тобі їх передали), чемно:
    — Покажи користувачу витягнуті дані.
    — Попроси перевірити їх і підтвердити, що все правильно.

    🔹 Після підтвердження даних:
    — Повідом вартість страхування. Вартість фіксована: 100 доларів США.
    — Напиши: "Ціна страхування становить 100 доларів США. Чи підходить вам така сума?"

    🔹 Якщо користувач ставить запитання, не пов'язане зі страхуванням авто — відповідай:
    “Я можу допомогти лише зі страхуванням авто.”

    🔹 Уникай канцеляризмів. Не використовуй шаблонні фрази. Будь живим і уважним.
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
