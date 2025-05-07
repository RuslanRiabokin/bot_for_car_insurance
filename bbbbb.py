import os
from uuid import uuid4
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

from ai_provider import ask_ai

router = Router()
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    response = ask_ai("Користувач розпочав діалог. Привітайся та попроси надіслати документи.")
    await message.answer(response)

@router.message(F.photo | F.document)
async def handle_documents(message: types.Message):
    user_id = message.from_user.id
    file = message.photo[-1] if message.photo else message.document
    file_name = f"{user_id}_{uuid4().hex}.jpg"
    path = os.path.join(TEMP_DIR, file_name)

    await message.bot.download(file, destination=path)

    # Повідомляємо AI, що отримали документ
    doc_type = "техпаспорт" if "тех" in file_name.lower() else "паспорт"
    response = ask_ai(f"Користувач надіслав фото {doc_type}. Що відповісти?")
    await message.answer(response)

@router.message(F.text)
async def handle_text(message: types.Message):
    await message.answer("🤖 Обробляю ваше повідомлення AI...")

    try:
        response = ask_ai(message.text)
    except Exception as e:
        await message.answer(f"❌ Помилка при зверненні до AI: {e}")
        return

    await message.answer(response.strip())
