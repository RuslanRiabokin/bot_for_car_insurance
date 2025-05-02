from services.mindee_service import extract_data_from_image_mock


def car_insurance_text(passport_path: str, reg_path: str) -> str:
    """
    Generates insurance policy text based on provided passport and vehicle registration images.

    Args:
        passport_path (str): Path to the passport image file.
        reg_path (str): Path to the vehicle registration image file.

    Returns:
        str: Generated insurance policy text.
    """
    data = extract_data_from_image_mock(passport_path, reg_path)
    return generate_insurance_text(data)


def generate_insurance_text(data: dict) -> str:
    """
    Generates insurance policy text using extracted data.

    Args:
        data (dict): Dictionary containing extracted fields such as 'ПІБ',
                     'Дата народження', 'Номер авто', and 'VIN'.

    Returns:
        str: Formatted insurance policy text.
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
