def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.

    Формат: XXXX XX** **** XXXX
    Показываются первые 6 и последние 4 цифры, остальные заменяются на *

    Args:
        card_number (str): Номер карты (16 цифр)

    Returns:
        str: Замаскированный номер карты

    Raises:
        ValueError: Если номер карты не состоит из 16 цифр
    """
    # Удаляем все пробелы и нецифровые символы
    cleaned_number = ''.join(filter(str.isdigit, card_number))

    # Проверяем, что номер состоит из 16 цифр
    if len(cleaned_number) != 16:
        raise ValueError("Номер карты должен содержать 16 цифр")

    # Маскируем номер: первые 6 и последние 4 цифры видимы, остальные *
    masked = (
            cleaned_number[:4] + ' ' +
            cleaned_number[4:6] + '** **** ' +
            cleaned_number[-4:]
    )

    return masked


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер банковского счета.

    Формат: **XXXX
    Показываются только последние 4 цифры, остальные заменяются на *

    Args:
        account_number (str): Номер счета

    Returns:
        str: Замаскированный номер счета

    Raises:
        ValueError: Если номер счета содержит меньше 4 цифр
    """
    # Удаляем все пробелы и нецифровые символы
    cleaned_number = ''.join(filter(str.isdigit, account_number))

    # Проверяем, что номер содержит хотя бы 4 цифры
    if len(cleaned_number) < 4:
        raise ValueError("Номер счета должен содержать минимум 4 цифры")

    # Маскируем номер: показываем только последние 4 цифры
    masked = '**' + cleaned_number[-4:]

    return masked