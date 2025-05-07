import os
from uuid import uuid4
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ai_provider import ask_ai

router = Router()
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Примітивне зберігання стану (в пам'яті)
user_states = {}  # user_id -> {"docs_received": 0}

def get_user_state(user_id: int) -> dict:
    if user_id not in user_states:
        user_states[user_id] = {"docs_received": 0}
    return user_states[user_id]

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_states[user_id] = {"docs_received": 0}

    response = ask_ai("Користувач розпочав діалог. Привітайся та попроси надіслати документи.")
    await message.answer(response)



@router.message(F.photo | F.document)
async def handle_documents(message: types.Message):
    user_id = message.from_user.id
    file = message.photo[-1] if message.photo else message.document
    file_name = f"{user_id}_{uuid4().hex}.jpg"
    path = os.path.join(TEMP_DIR, file_name)
    await message.bot.download(file, destination=path)

    # Отримуємо або ініціалізуємо стан
    state = user_states.setdefault(user_id, {"docs_received": 0, "extracted": False})
    state["docs_received"] += 1

    if state["docs_received"] == 1:
        prompt = (
            "Користувач надіслав перше фото — це паспорт. Подякуй за паспорт і скажи, "
            "що для оформлення автострахування потрібно ще надіслати фото техпаспорта."
        )
        response = ask_ai(prompt)
        await message.answer(response)

    elif state["docs_received"] == 2:
        state["extracted"] = True
        prompt = (
            "Користувач раніше надіслав фото паспорта. Тепер він надіслав фото техпаспорта. "
            "Подякуй за техпаспорт і скажи, що зараз витягуєш інформацію з обох документів для оформлення автострахування."
        )
        response = ask_ai(prompt)
        await message.answer(response)

        # Виводимо "витягнуті" (фіксовані) дані
        extracted_data = {
            "ПІБ": "Бондаренко Василий Васильевич",
            "Номер авто": "KE1234AE",
            "VIN": "VF1ABC1234567890",
            "Дата народження": "01.01.1990"
        }

        formatted_data = "\n".join(f"• {k}: {v}" for k, v in extracted_data.items())
        await message.answer(f"📄 Ось які дані вдалося витягнути з ваших документів:\n\n{formatted_data}")

        # Додаємо кнопки для підтвердження
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Підтвердити дані", callback_data="confirm_data")],
            [InlineKeyboardButton(text="❌ Дані не підходять", callback_data="reject_data")]
        ])
        await message.answer("Будь ласка, підтвердіть, чи все правильно:", reply_markup=keyboard)
    else:
        prompt = (
            "Користувач надіслав додаткове зображення після паспорта і техпаспорта. "
            "Подякуй за фото і скажи, що документи вже обробляються, нові зображення поки не потрібні."
        )
        response = ask_ai(prompt)
        await message.answer(response)


@router.callback_query(F.data == "reject_data")
async def handle_rejected_data(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Видаляємо файли користувача з папки temp
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(str(user_id)):
            file_path = os.path.join(TEMP_DIR, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Не вдалося видалити {file_path}: {e}")

    # Скидаємо стан
    user_states[user_id] = {"docs_received": 0, "extracted": False}

    # Відповідаємо користувачу
    await callback.message.answer("❌ Зрозуміло. Давайте спробуємо ще раз.\nБудь ласка, надішліть фото паспорта.")
    await callback.answer()  # закриває 'loading...' у Telegram


@router.callback_query(F.data == "confirm_data")
async def handle_confirmed_data(callback: CallbackQuery):
    user_id = callback.from_user.id

    # Видаляємо файли користувача з папки temp
    for filename in os.listdir(TEMP_DIR):
        if filename.startswith(str(user_id)):
            file_path = os.path.join(TEMP_DIR, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Не вдалося видалити {file_path}: {e}")

    # Генеруємо відповідь AI
    prompt = (
        "Користувач підтвердив правильність даних. "
        "Повідом, що фіксована вартість автострахування становить 100 доларів США. "
        "Дані користувача вже підтверджені, тому можна перейти до наступного кроку. "
        "Запропонуй користувачу обрати, що він хоче зробити далі: "
        "Оформити страховку або відмовитися через незгоду з ціною."
    )
    response = ask_ai(prompt)

    # Кнопки: Оформити / Вийти
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="📝 Оформити страховку", callback_data="proceed_insurance"),
            types.InlineKeyboardButton(text="🚪 Ні не згоден", callback_data="exit_bot"),
        ]
    ])

    await callback.message.answer(response, reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "proceed_insurance")
async def proceed_with_insurance(callback: CallbackQuery):
    await callback.message.answer("✅ Чудово! Переходимо до оформлення автострахування...")
    await callback.answer()

@router.callback_query(F.data == "exit_bot")
async def exit_bot(callback: CallbackQuery):
    await callback.message.answer("😔 Шкода, що ми не змогли допомогти. Якщо передумаєте — звертайтесь будь-коли!")
    await callback.answer()
