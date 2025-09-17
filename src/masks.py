def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    Формат: XXXX XX** **** XXXX
    """
    cleaned_number = "".join(filter(str.isdigit, card_number))
    if len(cleaned_number) != 16:
        return card_number  # Возвращаем исходную строку вместо исключения
    return f"{cleaned_number[:4]} {cleaned_number[4:6]}** **** {cleaned_number[-4:]}"


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер счета.
    Формат: **XXXX
    """
    cleaned_number = "".join(filter(str.isdigit, account_number))
    if len(cleaned_number) < 4:
        return account_number  # Возвращаем исходную строку
    return f"**{cleaned_number[-4:]}"