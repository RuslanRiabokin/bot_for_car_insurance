from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums.content_type import ContentType

from ai_states import AIAssistantState
from ai_provider import ask_ai

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AIAssistantState.waiting_for_documents)
    await state.update_data(documents=[], chat_history=[])
    await message.answer(
        "👋 Привіт! Я допоможу тобі з автострахуванням.\n\n"
        "Будь ласка, надішли фото паспорта 📄 та техпаспорта"
    )


@router.message(F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}))
async def handle_documents(message: Message, state: FSMContext):
    data = await state.get_data()
    documents = data.get("documents", [])

    file_id = message.document.file_id if message.document else message.photo[-1].file_id
    documents.append(file_id)
    await state.update_data(documents=documents)

    if len(documents) == 1:
        user_msg = "Я надіслав фото паспорта."
        ai_reply = await ask_ai(user_msg, state)
        await message.answer(ai_reply)

    elif len(documents) == 2:
        await state.set_state(AIAssistantState.documents_received)

        # Імітація витягнутих даних
        extracted_info = {
            "ПІБ": "Бондаренко Василь Васильович",
            "Номер авто": "KE1234AE",
            "VIN": "VF1ABC1234567890",
            "Дата народження": "01.01.1990"
        }
        await state.update_data(extracted_info=extracted_info)

        user_msg_2 = (
            "Ось дані, які я витягнув із ваших документів. Будь ласка, перевірте їх уважно.\n\n"
            f"ПІБ: {extracted_info['ПІБ']}\n"
            f"Номер авто: {extracted_info['Номер авто']}\n"
            f"VIN: {extracted_info['VIN']}\n"
            f"Дата народження: {extracted_info['Дата народження']}\n\n"
            "✅ Якщо все правильно — напишіть, що все вірно.\n"
            "❌ Якщо є помилка — вкажіть коректні дані для виправлення.\n\n"
            "Чекаю на ваш відповідь! 😊"
        )

        ai_reply_2 = await ask_ai(user_msg_2, state)
        await message.answer(ai_reply_2)

    else:
        user_msg = "Я надіслав ще одне фото."
        ai_reply = await ask_ai(user_msg, state)
        await message.answer(ai_reply)


@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    current_state = await state.get_state()
    text = message.text.strip().lower()

    if current_state == AIAssistantState.documents_received:
        if "підтверджую" in text or "все правильно" in text:
            await state.set_state(AIAssistantState.waiting_price_confirmation)
            ai_reply = await ask_ai("Користувач підтвердив правильність даних.", state)
            await message.answer(ai_reply)
            return

        elif "неправильно" in text or "помилка" in text:
            await message.answer("❌ Зрозуміло. Будь ласка, надішліть фото паспорта ще раз.")
            await state.set_state(AIAssistantState.waiting_for_documents)
            await state.update_data(documents=[], chat_history=[])
            await ask_ai("Користувач повідомив про помилку в даних. Починаю збір документів заново.", state)
            return

    elif current_state == AIAssistantState.waiting_price_confirmation:
        if "не згоден" in text or "не підходить" in text or "дорого" in text:
            await message.answer(
                "😔 На жаль, вартість у розмірі 100 доларів США є фіксованою.\n"
                "Інших варіантів наразі немає.\n\n"
                "Хочете завершити оформлення страхування чи все ж погоджуєтесь на цю ціну?"
            )
            await ask_ai(
                "Користувач не згоден з ціною. Поясни, що ціна фіксована, і запропонуй або погодитися, або завершити оформлення.",
                state
            )
            return

        if "згоден" in text or "підходить" in text or "добре" in text or "погоджуюсь" in text or "гаразд" in text:
            await state.set_state(AIAssistantState.policy_ready)
            await ask_ai("Користувач погодився на ціну. Переходь до етапу оформлення страхового полісу.", state)
            await message.answer("✅ Чудово! Тепер я сформую ваш страховий поліс. Очікуйте трохи...")
            return

        # Проміжна відповідь на будь-який інший текст
        ai_reply = await ask_ai(f"Користувач відповів на пропозицію щодо вартості: «{message.text}».", state)
        await message.answer(ai_reply)
        return

    # Загальний fallback: діалог з AI
    ai_reply = await ask_ai(message.text, state)
    await message.answer(ai_reply)
