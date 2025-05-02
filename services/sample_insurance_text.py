# sample_insurance_text.py
from services.mindee_service import extract_data_from_image_mock


def car_insurance_text(passport_path: str, reg_path: str) -> str:
    """
    Генерує текст страхового полісу на основі оброблених документів.
    """
    data = extract_data_from_image_mock(passport_path, reg_path)
    return generate_insurance_text(data)


def generate_insurance_text(data: dict) -> str:
    """
    Приймає словник з даними та формує текст страхового полісу.
    """
    pib = data.get("ПІБ", "Невідомо")
    birth_date = data.get("Дата народження", "Невідомо")
    car_number = data.get("Номер авто", "Невідомо")
    vin = data.get("VIN", "Невідомо")

    template = f"""
Страховий поліс №123456

Страхувальник: {pib}
Дата народження: {birth_date}

Дані про автомобіль:
Номер авто: {car_number}
VIN: {vin}

Цим підтверджується, що транспортний засіб застрахований відповідно до умов договору.
"""
    return template.strip()
