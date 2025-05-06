import re
from aiogram import Router, F, types
from aiogram.filters import Command
from ai_provider import ask_ai

router = Router()
user_states = {}

@router.message(Command("ask"))
async def cmd_ask_ai(message: types.Message):
    user_states[message.from_user.id] = "waiting_ai_question"
    await message.answer(
        "✍️ Напишіть ваше питання до AI (наприклад: *Які документи потрібні для страховки?*)",
        parse_mode="Markdown"
    )

@router.message(F.text)
async def handle_ai_question(message: types.Message):
    user_id = message.from_user.id
    if user_states.get(user_id) == "waiting_ai_question":
        question = message.text
        await message.answer("🤖 Думаю над відповіддю...")

        try:
            response = ask_ai(question)
        except Exception as e:
            await message.answer(f"❌ Помилка при зверненні до AI: {e}")
            return

        clean_response = re.sub(r"<!--.*?-->", "", response, flags=re.DOTALL)
        clean_response = re.sub(r"<[^>]+>", "", clean_response)

        await message.answer(clean_response.strip())
        user_states[user_id] = None
