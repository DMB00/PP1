"""
Тест подключения к Exchange Rates API
"""

from src.external_api import get_api_status, get_exchange_rate, convert_amount_to_rub


def test_api_connection():
    print("=== ТЕСТ ПОДКЛЮЧЕНИЯ К EXCHANGE RATES API ===")

    # Проверяем статус API
    status = get_api_status()

    if status:
        print("\nAPI доступно, тестируем конвертацию...")

        # Тестируем получение курса USD/RUB
        usd_rate = get_exchange_rate("USD", "RUB")
        if usd_rate:
            print(f" Текущий курс USD/RUB: {usd_rate}")

        # Тестируем получение курса EUR/RUB
        eur_rate = get_exchange_rate("EUR", "RUB")
        if eur_rate:
            print(f" Текущий курс EUR/RUB: {eur_rate}")

        # Тестируем конвертацию транзакции
        test_transaction = {
            "operationAmount": {
                "amount": "100.00",
                "currency": {"code": "USD"}
            }
        }

        result = convert_amount_to_rub(test_transaction)
        print(f" Конвертация 100 USD: {result:.2f} RUB")

    else:
        print("\n Проблемы с API:")
        print("   1. Проверьте наличие файла .env")
        print("   2. Проверьте правильность API ключа")
        print("   3. Проверьте подключение к интернету")
        print("   4. Убедитесь что подписка на API активна")


if __name__ == "__main__":
    test_api_connection()