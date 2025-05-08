from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.enums.content_type import ContentType

from ai_states import AIAssistantState
from ai_provider_2 import ask_ai

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(AIAssistantState.waiting_for_documents)
    await state.update_data(documents=[])  # створюємо список документів
    await state.update_data(chat_history=[])  # очищаємо історію спілкування
    await message.answer(
        "👋 Привіт! Я допоможу тобі з автострахуванням.\n\n"
        "Будь ласка, надішли фото паспорта 📄"
    )


@router.message(F.content_type.in_({ContentType.PHOTO, ContentType.DOCUMENT}))
async def handle_documents(message: Message, state: FSMContext):
    data = await state.get_data()
    documents = data.get("documents", [])

    # Определяем тип файла и сохраняем file_id
    file_id = (
        message.document.file_id if message.document
        else message.photo[-1].file_id
    )
    documents.append(file_id)
    await state.update_data(documents=documents)

    # Генерируем сообщение для AI
    if len(documents) == 1:
        user_msg = "Я надіслав фото паспорта."
    elif len(documents) == 2:
        user_msg = "Я надіслав фото техпаспорта."
        await state.set_state(AIAssistantState.documents_received)
    else:
        user_msg = "Я надіслав ще одне фото."

    # Получаем ответ от AI и отправляем пользователю
    ai_reply = await ask_ai(user_msg, state)
    await message.answer(ai_reply)


@router.message(F.text)
async def handle_text(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == AIAssistantState.waiting_for_documents:
        ai_reply = await ask_ai(message.text, state)
        await message.answer(
            f"{ai_reply}\n\n📎 Поки що надішли фото паспорта та техпаспорта, щоб я міг допомогти краще."
        )
    else:
        ai_reply = await ask_ai(message.text, state)
        await message.answer(ai_reply)
