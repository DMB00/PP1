"""
Модуль widget содержит функции для виджета операций.
"""

def mask_card_number(card_number: str) -> str:
    """Маскировка номера карты"""
    if not card_number:
        return ""

    card_str = str(card_number).replace(' ', '')
    if len(card_str) < 16:
        return str(card_number)

    return f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"


def mask_account_number(account_number: str) -> str:
    """Маскировка номера счета"""
    if not account_number:
        return ""

    account_str = str(account_number).replace(' ', '')
    if len(account_str) < 4:
        return str(account_number)

    return f"Счет **{account_str[-4:]}"