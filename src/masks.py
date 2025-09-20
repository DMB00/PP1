def get_mask_card_number(card_number: str) -> str:
    """Маскирует номер банковской карты."""
    if card_number is None:
        return ""

    # Если это не строка - возвращаем как есть (без маскировки)
    if not isinstance(card_number, str):
        return str(card_number)

    # Извлекаем только цифры
    digits = ""
    for char in card_number:
        if char in "0123456789":
            digits += char

    # Проверяем длину
    if len(digits) != 16:
        return card_number  # возвращаем исходную строку если не 16 цифр

    # Форматируем замаскированный номер
    return f"{digits[:4]} {digits[4:6]}** **** {digits[-4:]}"


def get_mask_account(account_number: str) -> str:
    """Маскирует номер счета."""
    if account_number is None:
        return ""

    # Если это не строка - возвращаем как есть (без маскировки)
    if not isinstance(account_number, str):
        return str(account_number)

    # Извлекаем только цифры
    digits = ""
    for char in account_number:
        if char in "0123456789":
            digits += char

    # Проверяем длину
    if len(digits) < 4:
        return account_number  # возвращаем исходную строку если меньше 4 цифр

    # Форматируем замаскированный номер
    return f"**{digits[-4:]}"