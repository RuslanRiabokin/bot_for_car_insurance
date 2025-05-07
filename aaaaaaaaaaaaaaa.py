import os
from uuid import uuid4
from aiogram import Router, F, types
from aiogram.filters import Command

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
    state = user_states.setdefault(user_id, {"docs_received": 0})
    state["docs_received"] += 1

    # Визначаємо, яке це фото
    if state["docs_received"] == 1:
        prompt = "Користувач надіслав фото паспорта. Подякуй і попроси техпаспорт."
    elif state["docs_received"] == 2:
        prompt = (
            "Користувач раніше надіслав паспорт. Тепер він надіслав фото техпаспорта. "
            "Подякуй за техпаспорт і скажи, що зараз витягуєш інформацію з обох документів для оформлення автострахування."
        )
    else:
        prompt = "Користувач надіслав ще одне зображення після обох документів. Подякуй і скажи, що документи вже обробляються."

    response = ask_ai(prompt)
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
