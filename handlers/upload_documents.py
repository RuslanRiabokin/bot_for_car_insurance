import os
from aiogram import Router, F
from aiogram.types import Message

router = Router()

# Простое хранение состояний (по user_id)
user_state = {}

# 📥 Команда /start
@router.message(F.text == "/start")
async def start_command(message: Message):
    user_state[message.from_user.id] = "waiting_for_passport"
    await message.answer("Привіт! Я допоможу оформити автостраховку. Спочатку надішліть фото паспорта 📷")

# 📸 Обработчик всех входящих фото
@router.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await message.answer("Будь ласка, спочатку натисніть /start.")
        return

    # Создаём папку temp/ если её нет
    TEMP_DIR = os.path.join(os.getcwd(), "temp")
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Берём самое качественное фото из списка
    photo = message.photo[-1]

    # Формируем путь для сохранения
    save_path = os.path.join(TEMP_DIR, f"{state}_{user_id}.jpg")

    # Сохраняем фото локально
    await message.bot.download(photo.file_id, destination=save_path)

    if state == "waiting_for_passport":
        user_state[user_id] = "waiting_for_registration"
        await message.answer("✅ Паспорт отримано. Тепер, будь ласка, надішліть фото техпаспорта 📄")
    elif state == "waiting_for_registration":
        user_state[user_id] = "done"
        await message.answer("✅ Техпаспорт отримано. Дякую! Тепер я перейду до обробки документів...")
