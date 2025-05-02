from typing import Dict

def extract_data_from_image_mock(passport_path: str, reg_path: str) -> Dict[str, str]:
    # Можна використовувати шляхи для логування або імітації
    return {
        "ПІБ": "Бондаренко Василий Васильевич ",
        "Номер авто": "KE1234AE",
        "VIN": "VF1ABC1234567890",
        "Дата народження": "01.01.1990"
    }
