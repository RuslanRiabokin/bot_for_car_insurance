from aiogram import Router, F
from aiogram.types import Message
import os
from aiofiles import open as aio_open

router = Router()

# Словник, щоб відслідковувати етапи користувача (можна замінити на FSM пізніше)
user_state = {}

@router.message(F.text == "/start")
async def start_command(message: Message):
    user_state[message.from_user.id] = "waiting_for_passport"
    await message.answer("Привіт! Я допоможу оформити автостраховку. Для початку, будь ласка, надішліть фото вашого паспорта.")


@router.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await message.answer("Будь ласка, спочатку натисніть /start.")
        return

    # Зберегти файл напряму
    photo = message.photo[-1]
    file_path = f"/tmp/{state}_{user_id}.jpg"
    await message.bot.download(photo.file_id, destination=file_path)

    if state == "waiting_for_passport":
        user_state[user_id] = "waiting_for_registration"
        await message.answer("✅ Паспорт отримано. Тепер, будь ласка, надішліть фото техпаспорта.")
    elif state == "waiting_for_registration":
        user_state[user_id] = "done"
        await message.answer("✅ Техпаспорт отримано. Дякую! Тепер я перейду до обробки документів...")

