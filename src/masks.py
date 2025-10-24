# src/masks.py
import logging


# Создаем простой логгер без конфигурации
def setup_logger(name, force_recreate=False):
    """Создает простой логгер"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = setup_logger('masks', force_recreate=True)


def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    Обрабатывает номера с пробелами, дефисами и другими разделителями.
    """
    logger.debug(f"Starting card number masking: {card_number}")

    # Обработка None и не-строк
    if card_number is None:
        logger.warning("None received for card masking")
        return ""

    if not isinstance(card_number, str):
        logger.warning(f"Non-string input received for card masking: {type(card_number)} - {card_number}")
        return str(card_number)

    # Обработка пустой строки
    if not card_number.strip():
        logger.warning("Empty string received for card masking")
        return card_number

    # Извлекаем только цифры из строки
    digits_only = ''.join(filter(str.isdigit, card_number))
    logger.debug(f"Extracted digits from card number: {digits_only}")

    # Проверяем длину цифрового номера
    if len(digits_only) != 16:
        logger.warning(
            f"Card number doesn't contain exactly 16 digits: {len(digits_only)} digits found in '{card_number}'")
        return card_number  # Возвращаем исходную строку если не 16 цифр

    try:
        # Форматируем маскированный номер
        masked_number = f"{digits_only[:4]} {digits_only[4:6]}** **** {digits_only[-4:]}"
        logger.info(f"Card masked successfully: {card_number} -> {masked_number}")
        return masked_number
    except Exception as e:
        logger.error(f"Error masking card {card_number}: {e}")
        return card_number  # Возвращаем исходную строку при ошибке


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер банковского счета.
    Обрабатывает номера с пробелами, дефисами, текстом и другими символами.
    """
    logger.debug(f"Starting account number masking: {account_number}")

    # Обработка None и не-строк
    if account_number is None:
        logger.warning("None received for account masking")
        return ""

    if not isinstance(account_number, str):
        logger.warning(f"Non-string input received for account masking: {type(account_number)} - {account_number}")
        return str(account_number)

    # Обработка пустой строки
    if not account_number.strip():
        logger.warning("Empty string received for account masking")
        return account_number

    # Извлекаем только цифры из строки
    digits_only = ''.join(filter(str.isdigit, account_number))
    logger.debug(f"Extracted digits from account number: {digits_only}")

    # Проверяем минимальную длину цифрового номера
    if len(digits_only) < 4:
        logger.warning(
            f"Account number doesn't contain at least 4 digits: {len(digits_only)} digits found in '{account_number}'")
        return account_number  # Возвращаем исходную строку если меньше 4 цифр

    try:
        # Форматируем маскированный номер
        masked_number = f"**{digits_only[-4:]}"
        logger.info(f"Account masked successfully: {account_number} -> {masked_number}")
        return masked_number
    except Exception as e:
        logger.error(f"Error masking account {account_number}: {e}")
        return account_number  # Возвращаем исходную строку при ошибке
