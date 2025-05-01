from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import openai
import os
from utils import fake_mindee_ocr, generate_policy_text

router = Router()
openai.api_key = os.getenv("OPENAI_API_KEY")


class Form(StatesGroup):
    waiting_for_passport = State()
    waiting_for_vehicle_doc = State()
    waiting_for_confirmation = State()
    waiting_for_price_agreement = State()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await message.answer("Привіт! Я бот, який допоможе вам придбати автострахування. Для початку, будь ласка, надішліть фото вашого паспорта.")
    await state.set_state(Form.waiting_for_passport)


@router.message(Form.waiting_for_passport, F.photo)
async def passport_handler(message: Message, state: FSMContext):
    passport_photo = message.photo[-1]
    await state.update_data(passport=passport_photo.file_id)
    await message.answer("Дякую. Тепер надішліть фото технічного паспорта на авто.")
    await state.set_state(Form.waiting_for_vehicle_doc)


@router.message(Form.waiting_for_vehicle_doc, F.photo)
async def vehicle_doc_handler(message: Message, state: FSMContext):
    vehicle_doc = message.photo[-1]
    await state.update_data(vehicle_doc=vehicle_doc.file_id)

    user_data = await state.get_data()
    extracted_data = fake_mindee_ocr()

    await state.update_data(extracted_data=extracted_data)

    await message.answer(f"Я розпізнав такі дані:\n"
                         f"<b>ПІБ:</b> {extracted_data['name']}\n"
                         f"<b>Номер авто:</b> {extracted_data['plate']}\n"
                         f"<b>VIN:</b> {extracted_data['vin']}\n"
                         f"<b>Дата народження:</b> {extracted_data['dob']}\n\n"
                         f"Ці дані правильні? (Так / Ні)")
    await state.set_state(Form.waiting_for_confirmation)


@router.message(Form.waiting_for_confirmation)
async def confirm_data(message: Message, state: FSMContext):
    if message.text.lower() == "ні":
        await message.answer("Будь ласка, повторно надішліть фото паспорта.")
        await state.set_state(Form.waiting_for_passport)
    elif message.text.lower() == "так":
        await message.answer("Ціна автострахування — <b>100 USD</b>. Ви згодні? (Так / Ні)")
        await state.set_state(Form.waiting_for_price_agreement)
    else:
        await message.answer("Будь ласка, відповідайте 'Так' або 'Ні'.")


@router.message(Form.waiting_for_price_agreement)
async def price_agreement(message: Message, state: FSMContext):
    if message.text.lower() == "ні":
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Напиши ввічливу відповідь, що ціна на автострахування 100 USD є фіксованою і не змінюється."}]
        )
        reply = response["choices"][0]["message"]["content"]
        await message.answer(reply)
    elif message.text.lower() == "так":
        data = await state.get_data()
        text = generate_policy_text(data["extracted_data"])
        await message.answer_document(document=("policy.txt", text.encode()), caption="Ось ваш страховий поліс. Дякуємо за покупку!")
        await state.clear()
    else:
        await message.answer("Будь ласка, відповідайте 'Так' або 'Ні'.")
