from datetime import datetime


def fake_mindee_ocr():
    # Мок розпізнавання
    return {
        "name": "Іван Іванов",
        "plate": "AA1234BB",
        "vin": "VF1ABC1234567890",
        "dob": "01.01.1990"
    }


def generate_policy_text(data: dict) -> str:
    return (
        f"Поліс автострахування\n"
        f"======================\n"
        f"ПІБ: {data['name']}\n"
        f"Номер авто: {data['plate']}\n"
        f"VIN: {data['vin']}\n"
        f"Дата народження: {data['dob']}\n"
        f"Дата оформлення: {datetime.now().strftime('%d.%m.%Y')}\n"
        f"Сума: 100 USD\n"
        f"Номер полісу: 123456789\n"
    )
