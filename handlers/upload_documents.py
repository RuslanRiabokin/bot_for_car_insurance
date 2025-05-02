import os
from aiogram import Router, F
from aiogram.types import FSInputFile
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.mindee_service import extract_data_from_image_mock

from services.policy_generator import generate_policy_pdf


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

def get_price_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так, згоден", callback_data="price_yes"),
            InlineKeyboardButton(text="❌ Ні", callback_data="price_no")
        ]
    ])

def get_price_retry_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Погоджуюсь", callback_data="price_yes"),
            InlineKeyboardButton(text="❌ Завершити оформлення", callback_data="cancel_process")
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

    # Переход к подтверждению стоимости
    user_state[user_id] = "waiting_price_confirmation"
    await callback.message.answer(
        "💵 Вартість автострахування становить <b>100 USD</b>.\nВи згодні з цією ціною?",
        parse_mode="HTML",
        reply_markup=get_price_keyboard()
    )


@router.callback_query(F.data == "reject_data")
async def handle_reject(callback: CallbackQuery):
    """Processing refusal and request to resend documents"""
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


@router.callback_query(F.data == "price_yes")
async def confirm_policy_and_send_pdf(callback: CallbackQuery):
    """Generates and sends the insurance policy PDF to the user"""
    user_id = callback.from_user.id
    await callback.message.edit_reply_markup()
    await callback.message.answer("✅ Дякую за підтвердження. Переходимо до генерації страхового полісу...")

    # Тимчасові шляхи до зображень
    temp_dir = os.path.join(os.getcwd(), "temp")
    passport_path = os.path.join(temp_dir, f"passport_{user_id}.jpg")
    reg_path = os.path.join(temp_dir, f"registration_{user_id}.jpg")

    # Створення PDF
    pdf_path = os.path.join(temp_dir, f"policy_{user_id}.pdf")
    generate_policy_pdf(passport_path, reg_path, pdf_path)

    # Надсилання PDF
    if os.path.exists(pdf_path):
        pdf_input = FSInputFile(pdf_path)
        await callback.message.answer_document(pdf_input, caption="📄 Ось ваш страховий поліс")
    else:
        await callback.message.answer(
            "Помилка: не вдалося знайти PDF файл страхового полісу. Спробуйте ще раз або зверніться до підтримки.")

    # Очищення
    for file in [passport_path, reg_path, pdf_path]:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

    user_state[user_id] = None

# ❌ Користувач не згоден з ціною
@router.callback_query(F.data == "price_no")
async def handle_price_no(callback: CallbackQuery):
    user_state[callback.from_user.id] = "price_rejected"
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "😔 Вибачте, ціна <b>фіксована</b> і не підлягає зміні.\n\n"
        "Бажаєте все ж погодитись чи завершити оформлення?",
        parse_mode="HTML",
        reply_markup=get_price_retry_keyboard()
    )

# ❌ Завершення оформлення
@router.callback_query(F.data == "cancel_process")
async def handle_cancel(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_state.pop(user_id, None)
    await callback.message.edit_reply_markup()
    await callback.message.answer("🚫 Оформлення страховки скасовано. Якщо передумаєте — напишіть /start.")
