def filter_by_currency(transactions, currency):
    """
    Фильтрует транзакции по заданной валюте.

    Args:
        transactions: список словарей с транзакциями
        currency: код валюты для фильтрации (например, "USD")

    Yields:
        dict: транзакции с заданной валютой
    """
    for transaction in transactions:
        try:
            if transaction['operationAmount']['currency']['code'] == currency:
                yield transaction
        except (KeyError, TypeError):
            # Пропускаем транзакции с некорректной структурой
            continue


def transaction_descriptions(transactions):
    """
    Генератор, который возвращает описание каждой транзакции по очереди.

    Args:
        transactions: список словарей с транзакциями

    Yields:
        str: описание транзакции
    """
    for transaction in transactions:
        yield transaction['description']


def card_number_generator(start, end):
    """
    Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

    Args:
        start: начальный номер (от 1 до 9999)
        end: конечный номер (от 1 до 9999, должен быть >= start)

    Yields:
        str: номер карты в формате XXXX XXXX XXXX XXXX
    """
    for number in range(start, end + 1):
        # Форматируем номер с ведущими нулями до 16 цифр
        card_number = str(number).zfill(16)
        # Разбиваем на группы по 4 цифры
        formatted_number = ' '.join([card_number[i:i + 4] for i in range(0, 16, 4)])
        yield formatted_number


def filter_by_currency(transactions: list, currency: str):
    """
    Фильтрует транзакции по заданной валюте и возвращает итератор-генератор.

    Args:
        transactions: список словарей с транзакциями
        currency: код валюты для фильтрации (например, "USD")

    Yields:
        dict: транзакции с заданной валютой
    """
    for transaction in transactions:
        operation_amount = transaction.get('operationAmount', {})
        currency_info = operation_amount.get('currency', {})
        if currency_info.get('code') == currency:
            yield transaction

        def transaction_descriptions(transactions: list):
            """
            Генератор, который возвращает описание каждой транзакции по очереди.

            Args:
                transactions: список словарей с транзакциями

            Yields:
                str: описание транзакции
            """
            for transaction in transactions:
                yield transaction['description']

            def card_number_generator(start: int, end: int):
                """
                Генератор номеров банковских карт в формате XXXX XXXX XXXX XXXX.

                Args:
                    start: начальный номер (от 1 до 9999999999999999)
                    end: конечный номер (должен быть >= start)

                Yields:
                    str: номер карты в формате XXXX XXXX XXXX XXXX
                """
                for number in range(start, end + 1):
                    # Форматируем номер с ведущими нулями до 16 цифр
                    card_number = str(number).zfill(16)
                    # Разбиваем на группы по 4 цифры с пробелами
                    formatted_number = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:16]}"
                    yield formatted_number