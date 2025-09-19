def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    Извлекает все цифры из входных данных и маскирует их.

    Args:
        card_number: Номер карты в любом формате (строка, число, с символами)

    Returns:
        str: Замаскированный номер карты в формате XXXX XX** **** XXXX
              или исходная строка если не удалось извлечь 16 цифр
    """
    if card_number is None:
        return ""

    # Преобразуем в строку и извлекаем только цифры
    card_str = str(card_number)
    digits = "".join(char for char in card_str if char.isdigit())

    # Проверяем, что удалось извлечь ровно 16 цифр
    if len(digits) == 16:
        return f"{digits[:4]} {digits[4:6]}** **** {digits[-4:]}"
    else:
        # Возвращаем исходную строку если не 16 цифр
        return card_str


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер счета.
    Извлекает все цифры из входных данных и маскирует их.

    Args:
        account_number: Номер счета в любом формате (строка, число, с символами)

    Returns:
        str: Замаскированный номер счета в формате **XXXX
              или исходная строка если не удалось извлечь минимум 4 цифры
    """
    if account_number is None:
        return ""

    # Преобразуем в строку и извлекаем только цифры
    account_str = str(account_number)
    digits = "".join(char for char in account_str if char.isdigit())

    # Проверяем, что удалось извлечь минимум 4 цифры
    if len(digits) >= 4:
        return f"**{digits[-4:]}"
    else:
        # Возвращаем исходную строку если меньше 4 цифр
        return account_str