from datetime import datetime
from .masks import get_mask_card_number, get_mask_account


def mask_account_card(account_info: str) -> str:
    """Маскирует номер счета или карты в переданной строке."""
    if not account_info:
        return ""

    if "Счет" in account_info:
        account_number = account_info.split("Счет")[-1].strip()
        masked_number = get_mask_account(account_number)
        return f"Счет {masked_number}"
    else:
        # Ищем цифровую часть
        digits = ''.join(filter(str.isdigit, account_info))
        if not digits:
            return account_info

        masked_number = get_mask_card_number(digits)

        # Сохраняем текстовую часть
        text_part = ''.join(filter(lambda x: not x.isdigit(), account_info)).strip()

        return f"{text_part} {masked_number}"


def get_date(date_string: str) -> str:
    """
    Преобразует дату из формата ISO в формат DD.MM.YYYY
    """
    if date_string is None:
        raise TypeError("Дата не может быть None")

    try:
        # Обрабатываем различные форматы
        if 'T' in date_string:
            date_part = date_string.split('T')[0]
        else:
            date_part = date_string

        # Парсим дату
        year, month, day = date_part.split('-')
        return f"{int(day):02d}.{int(month):02d}.{year}"

    except (ValueError, AttributeError, TypeError) as e:
        raise ValueError(f"Неверный формат даты: {date_string}") from e