import os
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.mindee_service import extract_data_from_image_mock

router = Router()

# Простое хранение состояний (по user_id)
user_state = {}

def get_confirmation_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_data"),
            InlineKeyboardButton(text="❌ Змінити", callback_data="reject_data")
        ]
    ])

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

    photo = message.photo[-1]

    if state == "waiting_for_passport":
        passport_path = os.path.join(TEMP_DIR, f"passport_{user_id}.jpg")
        await message.bot.download(photo.file_id, destination=passport_path)
        user_state[user_id] = "waiting_for_registration"
        await message.answer("✅ Паспорт отримано. Тепер, будь ласка, надішліть фото техпаспорта 📄")

    elif state == "waiting_for_registration":
        reg_path = os.path.join(TEMP_DIR, f"registration_{user_id}.jpg")
        await message.bot.download(photo.file_id, destination=reg_path)
        user_state[user_id] = "confirming"

        # Пути к обоим изображениям
        passport_path = os.path.join(TEMP_DIR, f"passport_{user_id}.jpg")
        reg_path = os.path.join(TEMP_DIR, f"registration_{user_id}.jpg")

        extracted_data = extract_data_from_image_mock(passport_path, reg_path)
        formatted = "\n".join([f"<b>{k}</b>: {v}" for k, v in extracted_data.items()])
        await message.answer(
            f"🔍 Ось що вдалося витягти з документів:\n\n{formatted}\n\nПідтвердіть, будь ласка.",
            parse_mode="HTML",
            reply_markup=get_confirmation_keyboard()
        )

# ✅ Обработка подтверждения данных
@router.callback_query(F.data == "confirm_data")
async def handle_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_state[user_id] = "confirmed"

    # Удаляем клавиатуру
    await callback.message.edit_reply_markup()

    # Удаляем файлы
    temp_dir = os.path.join(os.getcwd(), "temp")
    for doc in ["passport", "registration"]:
        try:
            os.remove(os.path.join(temp_dir, f"{doc}_{user_id}.jpg"))
        except FileNotFoundError:
            pass

    await callback.message.answer("✅ Дані підтверджено. Переходимо до наступного кроку...")


# ❌ Обработка отказа и просьба переслать документы заново
@router.callback_query(F.data == "reject_data")
async def handle_reject(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_state[user_id] = "waiting_for_passport"

    # Удаление старых фото
    temp_dir = os.path.join(os.getcwd(), "temp")
    for doc in ["passport", "registration"]:
        try:
            os.remove(os.path.join(temp_dir, f"{doc}_{user_id}.jpg"))
        except FileNotFoundError:
            pass

    await callback.message.edit_reply_markup()
    await callback.message.answer("❌ Зрозуміло. Будь ласка, знову надішліть фото паспорта 📷")
