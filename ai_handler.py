import logging
import os
import re

from aiogram import Router, F
from aiogram.enums.content_type import ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from ai_provider import ask_ai, reset_chat_history
from ai_states import AIAssistantState
from services.pdf_generator import generate_insurance_pdf

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

    file_id = (
        message.document.file_id if message.document else message.photo[-1].file_id
    )
    documents.append(file_id)
    await state.update_data(documents=documents)

    if len(documents) == 1:
        ai_reply = await ask_ai("Користувач надіслав фото паспорта.", state)
        await message.answer(ai_reply)

    elif len(documents) == 2:
        await state.set_state(AIAssistantState.documents_received)

        extracted_info = {
            "ПІБ": "Бондаренко Василь Васильович",
            "Номер авто": "KE1234AE",
            "VIN": "VF1ABC1234567890",
            "Дата народження": "01.01.1990"
        }
        await state.update_data(extracted_info=extracted_info)

        confirmation_msg = (
            "Ось дані, які я витягнув із ваших документів. Будь ласка, перевірте їх уважно.\n\n"
            f"ПІБ: {extracted_info['ПІБ']}\n"
            f"Номер авто: {extracted_info['Номер авто']}\n"
            f"VIN: {extracted_info['VIN']}\n"
            f"Дата народження: {extracted_info['Дата народження']}\n\n"
            "✅ Якщо все правильно — напишіть, що все вірно.\n"
            "❌ Якщо є помилка — вкажіть коректні дані для виправлення.\n\n"
            "Чекаю на ваш відповідь! 😊"
        )

        ai_reply = await ask_ai(confirmation_msg, state)
        await message.answer(ai_reply)

    else:
        ai_reply = await ask_ai("Користувач надіслав ще одне фото.", state)
        await message.answer(ai_reply)


@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    text = message.text.strip()

    ai_reply = await ask_ai(text, state)
    await message.answer(ai_reply)

    # Проверяем, содержит ли ответ фразу о формировании полісу
    if re.search(r"формую.*страховий поліс", ai_reply.lower()):
        await send_pdf(message, state)

async def send_pdf(message: Message, state: FSMContext):
    logging.info(f"[DEBUG] Входжу у send_pdf()")

    data = await state.get_data()
    extracted_info = data.get("extracted_info")

    if not extracted_info:
        await message.answer("⚠️ Дані для полісу відсутні. Спробуйте спочатку.")
        return

    # Генеруємо поліс у тимчасовий файл
    pdf_path = generate_insurance_pdf(extracted_info)
    logging.info(f"[DEBUG] PDF згенеровано: {pdf_path}")

    try:
        input_file = FSInputFile(pdf_path)
        await message.answer("📤 Надсилаю ваш страховий поліс...")
        await message.answer_document(document=input_file, caption="📄 Ваш страховий поліс готовий!")

    except Exception as e:
        logging.exception("Помилка при надсиланні PDF:")
        await message.answer(f"❗ Помилка при надсиланні PDF:\n{str(e)}", parse_mode="Markdown")

    finally:
        # Видаляємо тимчасовий файл
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            logging.info(f"[DEBUG] Тимчасовий PDF видалено: {pdf_path}")

        await reset_chat_history(state)
        await state.clear()
        logging.info("[DEBUG] Стан очищено")
