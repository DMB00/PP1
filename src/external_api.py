"""
Модуль external_api содержит функции для работы с внешними API.
"""

import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


def get_exchange_rate(from_currency: str, to_currency: str = "RUB") -> Optional[float]:
    """
    Получает текущий курс валюты через Exchange Rates Data API.

    Args:
        from_currency: исходная валюта (например, "USD", "EUR")
        to_currency: целевая валюта (по умолчанию "RUB")

    Returns:
        Optional[float]: курс обмена или None в случае ошибки
    """
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")

    if not api_key:
        print("Ошибка: API ключ не найден в переменных окружения")
        print("Создайте файл .env с EXCHANGE_RATES_API_KEY=ваш_ключ")
        return None

    if from_currency == to_currency:
        return 1.0

    # URL для конвертации валют
    url = "https://api.apilayer.com/exchangerates_data/convert"

    try:
        print(f"Получение курса {from_currency} -> {to_currency}...")

        response = requests.get(
            url,
            params={
                "from": from_currency,
                "to": to_currency,
                "amount": 1  # Конвертируем 1 единицу для получения курса
            },
            headers={
                "apikey": api_key
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            rate = data.get("result")
            print(f"Курс {from_currency}/{to_currency}: {rate}")
            return rate
        else:
            print(f"Ошибка API: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Ошибка подключения к API: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None


def convert_amount_to_rub(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction: словарь с данными транзакции

    Returns:
        float: сумма в рублях
    """
    try:
        operation_amount = transaction.get("operationAmount", {})
        amount_str = operation_amount.get("amount", "0")
        currency_info = operation_amount.get("currency", {})
        currency_code = currency_info.get("code", "RUB")

        # Преобразуем строку в float
        amount = float(amount_str)

        # Если уже в рублях, возвращаем как есть
        if currency_code == "RUB":
            return amount

        # Если USD или EUR, конвертируем через API
        if currency_code in ["USD", "EUR"]:
            print(f"Конвертация {amount} {currency_code} в RUB...")
            exchange_rate = get_exchange_rate(currency_code, "RUB")

            if exchange_rate:
                result = amount * exchange_rate
                print(f"Результат конвертации: {result:.2f} RUB")
                return result
            else:
                print(f"Не удалось получить курс {currency_code}, возвращаем исходную сумму")
                return amount

        # Для других валют возвращаем как есть
        print(f"Валюта {currency_code} не поддерживается для конвертации")
        return amount

    except (ValueError, TypeError) as e:
        print(f"Ошибка преобразования суммы: {e}")
        return 0.0
    except Exception as e:
        print(f"Неожиданная ошибка при конвертации: {e}")
        return 0.0


# Кэш для курсов валют (чтобы уменьшить количество запросов к API)
_exchange_rate_cache: Dict[str, float] = {}


def get_exchange_rate_cached(from_currency: str, to_currency: str = "RUB") -> Optional[float]:
    """
    Получает курс валюты с кэшированием.

    Args:
        from_currency: исходная валюта
        to_currency: целевая валюта

    Returns:
        Optional[float]: курс обмена или None
    """
    cache_key = f"{from_currency}_{to_currency}"

    # Проверяем кэш
    if cache_key in _exchange_rate_cache:
        print(f"Используем кэшированный курс: {_exchange_rate_cache[cache_key]}")
        return _exchange_rate_cache[cache_key]

    # Получаем курс из API
    rate = get_exchange_rate(from_currency, to_currency)

    # Кэшируем только если курс получен успешно (не None)
    if rate is not None:
        _exchange_rate_cache[cache_key] = rate
        print(f"Сохраняем в кэш: {rate}")

    return rate


def clear_exchange_rate_cache():
    """
    Очищает кэш курсов валют.
    Используется в тестах для изоляции.
    """
    global _exchange_rate_cache
    _exchange_rate_cache.clear()
    print("Кэш очищен")


def get_api_status() -> bool:
    """
    Проверяет доступность API и валидность ключа.

    Returns:
        bool: True если API доступно, False если нет
    """
    api_key = os.getenv("EXCHANGE_RATES_API_KEY")

    if not api_key:
        print("API ключ не найден")
        return False

    url = "https://api.apilayer.com/exchangerates_data/latest"

    try:
        response = requests.get(
            url,
            params={"base": "USD"},
            headers={"apikey": api_key},
            timeout=10
        )

        if response.status_code == 200:
            print(" API доступно и ключ валиден")
            return True
        else:
            print(f" Ошибка API: {response.status_code}")
            return False

    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return False
