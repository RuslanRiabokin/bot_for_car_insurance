import os
from aiogram import Router, F
from aiogram.types import Message
from services.mindee_service import extract_data_from_image_mock

router = Router()
user_state = {}

@router.message(F.text == "/start")
async def start_command(message: Message):
    user_state[message.from_user.id] = "waiting_for_passport"
    await message.answer("Привіт! Я допоможу оформити автостраховку. Спочатку надішліть фото паспорта 📷")

@router.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await message.answer("Будь ласка, спочатку натисніть /start.")
        return

    TEMP_DIR = os.path.join(os.getcwd(), "temp")
    os.makedirs(TEMP_DIR, exist_ok=True)

    photo = message.photo[-1]

    if state == "waiting_for_passport":
        passport_path = os.path.join(TEMP_DIR, f"passport_{user_id}.jpg")
        await message.bot.download(photo.file_id, destination=passport_path)
        user_state[user_id] = "waiting_for_registration"
        await message.answer("✅ Паспорт отримано. Тепер, будь ласка, надішліть фото техпаспорта 📄")

    elif state == "waiting_for_registration":
        reg_path = os.path.join(TEMP_DIR, f"registration_{user_id}.jpg")
        await message.bot.download(photo.file_id, destination=reg_path)

        user_state[user_id] = "done"
        await message.answer("✅ Техпаспорт отримано. Дякую! Обробляю документи... 🔄")

        # Виклик мок-функції
        extracted_data = extract_data_from_image_mock(
            passport_path=os.path.join(TEMP_DIR, f"passport_{user_id}.jpg"),
            reg_path=reg_path
        )

        formatted = "\n".join([f"<b>{k}</b>: {v}" for k, v in extracted_data.items()])
        await message.answer(f"🔍 Ось що вдалося витягти з документів:\n\n{formatted}\n\nПідтвердіть, будь ласка.", parse_mode="HTML")
