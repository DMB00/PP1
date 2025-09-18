def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    Извлекает цифры из входной строки и маскирует их.
    """
    if card_number is None:
        return ""

    # Извлекаем только цифры из входной строки
    cleaned_number = "".join(filter(str.isdigit, str(card_number)))

    # Проверяем, что номер состоит из 16 цифр
    if len(cleaned_number) != 16:
        return str(card_number)  # возвращаем исходную строку если не 16 цифр

    # Форматируем замаскированный номер
    return f"{cleaned_number[:4]} {cleaned_number[4:6]}** **** {cleaned_number[-4:]}"


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер счета.
    Извлекает цифры из входной строки и маскирует их.
    """
    if account_number is None:
        return ""

    # Извлекаем только цифры из входной строки
    cleaned_number = "".join(filter(str.isdigit, str(account_number)))

    # Проверяем, что номер состоит хотя бы из 4 цифр
    if len(cleaned_number) < 4:
        return str(account_number)  # возвращаем исходную строку если меньше 4 цифр

    # Форматируем замаскированный номер
    return f"**{cleaned_number[-4:]}"