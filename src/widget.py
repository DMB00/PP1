#функция mask_account_card
def mask_account_card(account_info: str) -> str:
    # Импорт существующей функции маскировки
    from .main import get_mask_card_number, get_mask_account
    # раздиление строки на части
    parts = account_info.split()

    if not parts:
        raise ValueError("Передана пустая строка")

    # извлечение номера (последний элемент)
    number_str = parts[-1]

    # проверка
    if not number_str.isdigit():
        raise ValueError("Номер карты/счета должен содержать только цифры")

    # Определение типа по длине номера
    if len(number_str) == 16:
        masked_number = get_mask_card_number(number_str)
        return account_info.replace(number_str, masked_number)

    elif len(number_str) >= 4:  # Номер счета (минимум 4 цифры)
        # Проверка, что в строке есть указание на счёт
        if "счет" in account_info.lower() or "account" in account_info.lower():
            masked_number = get_mask_account(number_str)
            return account_info.replace(number_str, masked_number)
        else:
            # Если нет указания на счет, но номер длинный - будет счет
            masked_number = get_mask_account(number_str)
            return account_info.replace(number_str, masked_number)

    else:
        raise ValueError(f"Неизвестный формат номера: {number_str}")

    #функция get_date
    from datetime import datetime

    def get_date(date_string: str) -> str:
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%d.%m.%Y")

        except (ValueError, AttributeError) as e:
            raise ValueError(
                f"Неверный формат даты: {date_string}. Ожидается: 'YYYY-MM-DDTHH:MM:SS.microseconds'") from e