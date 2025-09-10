def mask_card_number(card_number: str) -> str:
    """Маскирует номер карты."""
    cleaned_number = "".join(filter(str.isdigit, card_number))
    if len(cleaned_number) != 16:
        return card_number
    return f"{cleaned_number[:4]} {cleaned_number[4:6]}** **** {cleaned_number[-4:]}"


def mask_account_number(account_number: str) -> str:
    """Маскирует номер счета."""
    cleaned_number = "".join(filter(str.isdigit, account_number))
    if len(cleaned_number) < 4:
        return account_number
    return f"**{cleaned_number[-4:]}"


def mask_account_card(account_info: str) -> str:
    """Маскирует номер счета или карты в переданной строке."""
    if "Счет" in account_info:
        account_number = account_info.split("Счет")[-1].strip()
        masked_number = mask_account_number(account_number)
        return f"Счет {masked_number}"
    else:
        for part in reversed(account_info.split()):
            if part.isdigit():
                card_number = part
                break
        else:
            card_number = account_info

        masked_number = mask_card_number(card_number)
        card_name = account_info.rsplit(card_number, 1)[0].strip()

        return f"{card_name} {masked_number}"
