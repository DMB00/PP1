from .logger_config import setup_logger

# Создаем логгер для модуля masks с принудительным пересозданием
logger = setup_logger('masks', force_recreate=True)


def get_mask_card_number(card_number: str) -> str:
    """
    Маскирует номер банковской карты.
    """
    logger.debug(f"Starting card number masking: {card_number}")

    if not card_number:
        logger.warning("Empty string received for card masking")
        return ""

    if len(card_number) != 16 or not card_number.isdigit():
        logger.error(f"Invalid card number: {card_number}")
        raise ValueError("Card number must contain 16 digits")

    try:
        masked_number = f"{card_number[:4]} {card_number[4:6]}** **** {card_number[-4:]}"
        logger.info(f"Card masked successfully: {card_number} -> {masked_number}")
        return masked_number
    except Exception as e:
        logger.error(f"Error masking card {card_number}: {e}")
        raise


def get_mask_account(account_number: str) -> str:
    """
    Маскирует номер банковского счета.
    """
    logger.debug(f"Starting account number masking: {account_number}")

    if not account_number:
        logger.warning("Empty string received for account masking")
        return ""

    if len(account_number) < 4 or not account_number.isdigit():
        logger.error(f"Invalid account number: {account_number}")
        raise ValueError("Account number must contain at least 4 digits")

    try:
        masked_number = f"**{account_number[-4:]}"
        logger.info(f"Account masked successfully: {account_number} -> {masked_number}")
        return masked_number
    except Exception as e:
        logger.error(f"Error masking account {account_number}: {e}")
        raise
