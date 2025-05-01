import os
from aiogram.types import Message
from aiogram import Router, F
from aiogram.enums.content_type import ContentType

passport_router = Router()

@passport_router.message(F.content_type == ContentType.PHOTO)
async def handle_passport_photo(message: Message):
    TEMP_DIR = os.path.join(os.getcwd(), "temp")
    os.makedirs(TEMP_DIR, exist_ok=True)

    user_id = message.from_user.id
    photo = message.photo[-1]  # найякісніше зображення

    photo_path = os.path.join(TEMP_DIR, f"waiting_for_passport_{user_id}.jpg")
    await photo.download(destination_file=photo_path)

    await message.answer(f"Фото паспорта збережено: {photo_path}")
