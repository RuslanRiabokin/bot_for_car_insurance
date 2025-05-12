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

        # Формуємо повідомлення з даними, які треба підтвердити
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

    # Якщо вже отримано 2 документи і чекаємо підтвердження
    if current_state == AIAssistantState.documents_received:
        if "підтверджую" in text or "все правильно" in text:
            await message.answer("✅ Дякую за підтвердження! Тепер я можу перейти до оформлення поліса.")
            await ask_ai("Користувач підтвердив коректність даних.", state)
            return

        elif "хочу змінити" in text or "неправильно" in text or "помилка" in text:
            await message.answer("❌ Зрозуміло. Будь ласка, надішліть фото паспорта ще раз.")
            await state.set_state(AIAssistantState.waiting_for_documents)
            await state.update_data(documents=[], chat_history=[])
            await ask_ai("Користувач повідомив про помилку в даних. Починаю збір документів заново.", state)
            return

    # Звичайне повідомлення
    ai_reply = await ask_ai(message.text, state)
    await message.answer(ai_reply)
