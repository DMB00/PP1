"""
Тесты для модуля external_api.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.external_api import (
    get_exchange_rate,
    convert_amount_to_rub,
    get_exchange_rate_cached
)


class TestExchangeRateAPI:
    """Тесты для функций работы с API курсов валют."""

    @patch('src.external_api.requests.get')
    @patch('src.external_api.os.getenv')
    def test_get_exchange_rate_success(self, mock_getenv, mock_requests_get):
        """Тест успешного получения курса валют."""
        # Мокаем API ключ
        mock_getenv.return_value = "test_api_key"

        # Мокаем успешный ответ API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 75.5}
        mock_requests_get.return_value = mock_response

        result = get_exchange_rate("USD", "RUB")

        assert result == 75.5
        mock_requests_get.assert_called_once()

    @patch('src.external_api.requests.get')
    @patch('src.external_api.os.getenv')
    def test_get_exchange_rate_api_error(self, mock_getenv, mock_requests_get):
        """Тест обработки ошибки API."""
        mock_getenv.return_value = "test_api_key"

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_requests_get.return_value = mock_response

        result = get_exchange_rate("USD", "RUB")

        assert result is None

    @patch('src.external_api.requests.get')
    @patch('src.external_api.os.getenv')
    def test_get_exchange_rate_connection_error(self, mock_getenv, mock_requests_get):
        """Тест обработки ошибки подключения."""
        mock_getenv.return_value = "test_api_key"
        mock_requests_get.side_effect = Exception("Connection error")

        result = get_exchange_rate("USD", "RUB")

        assert result is None

    @patch('src.external_api.requests.get')
    @patch('src.external_api.os.getenv')
    def test_get_exchange_rate_same_currency(self, mock_getenv, mock_requests_get):
        """Тест конвертации одинаковых валют."""
        # Мокаем API ключ
        mock_getenv.return_value = "test_api_key"

        # Для одинаковых валют не должно быть вызова API
        result = get_exchange_rate("RUB", "RUB")

        assert result == 1.0
        # Убеждаемся что API не вызывалось для одинаковых валют
        mock_requests_get.assert_not_called()

    @patch('src.external_api.os.getenv')
    def test_get_exchange_rate_no_api_key(self, mock_getenv):
        """Тест отсутствия API ключа."""
        mock_getenv.return_value = None

        result = get_exchange_rate("USD", "RUB")

        assert result is None


class TestConvertAmountToRub:
    """Тесты для функции конвертации суммы в рубли."""

    def test_convert_rub_transaction(self):
        """Тест конвертации транзакции в рублях."""
        transaction = {
            "operationAmount": {
                "amount": "1000.50",
                "currency": {"code": "RUB"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 1000.50

    @patch('src.external_api.get_exchange_rate')
    def test_convert_usd_transaction(self, mock_get_rate):
        """Тест конвертации транзакции в USD."""
        mock_get_rate.return_value = 75.5

        transaction = {
            "operationAmount": {
                "amount": "100.00",
                "currency": {"code": "USD"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 7550.0  # 100 * 75.5
        mock_get_rate.assert_called_once_with("USD", "RUB")

    @patch('src.external_api.get_exchange_rate')
    def test_convert_eur_transaction(self, mock_get_rate):
        """Тест конвертации транзакции в EUR."""
        mock_get_rate.return_value = 85.2

        transaction = {
            "operationAmount": {
                "amount": "50.00",
                "currency": {"code": "EUR"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 4260.0  # 50 * 85.2
        mock_get_rate.assert_called_once_with("EUR", "RUB")

    @patch('src.external_api.get_exchange_rate')
    def test_convert_with_api_error(self, mock_get_rate):
        """Тест конвертации при ошибке API."""
        mock_get_rate.return_value = None

        transaction = {
            "operationAmount": {
                "amount": "100.00",
                "currency": {"code": "USD"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 100.0  # Возвращает исходную сумму

    def test_convert_unsupported_currency(self):
        """Тест конвертации неподдерживаемой валюты."""
        transaction = {
            "operationAmount": {
                "amount": "100.00",
                "currency": {"code": "GBP"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 100.0

    def test_convert_invalid_amount(self):
        """Тест конвертации с невалидной суммой."""
        transaction = {
            "operationAmount": {
                "amount": "invalid",
                "currency": {"code": "RUB"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 0.0

    def test_convert_missing_operation_amount(self):
        """Тест конвертации транзакции без operationAmount."""
        transaction = {"id": 1}

        result = convert_amount_to_rub(transaction)
        assert result == 0.0

    def test_convert_missing_currency(self):
        """Тест конвертации транзакции без валюты."""
        transaction = {
            "operationAmount": {
                "amount": "100.00"
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 100.0  # По умолчанию RUB

    def test_convert_empty_currency(self):
        """Тест конвертации транзакции с пустой валютой."""
        transaction = {
            "operationAmount": {
                "amount": "100.00",
                "currency": {}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 100.0  # По умолчанию RUB


class TestExchangeRateCached:
    """Тесты для кэширования курсов валют."""

    def setup_method(self):
        """Очищаем кэш перед каждым тестом."""
        from src.external_api import clear_exchange_rate_cache
        clear_exchange_rate_cache()

    @patch('src.external_api.get_exchange_rate')
    def test_get_exchange_rate_cached(self, mock_get_rate):
        """Тест кэширования курса валют."""
        mock_get_rate.return_value = 75.5

        # Первый вызов - должен вызвать API
        result1 = get_exchange_rate_cached("USD", "RUB")
        assert result1 == 75.5
        assert mock_get_rate.call_count == 1

        # Второй вызов - должен вернуть из кэша
        result2 = get_exchange_rate_cached("USD", "RUB")
        assert result2 == 75.5
        assert mock_get_rate.call_count == 1  # Все еще 1 вызов

    @patch('src.external_api.get_exchange_rate')
    def test_get_exchange_rate_cached_different_currencies(self, mock_get_rate):
        """Тест кэширования разных валютных пар."""
        # Используем side_effect для разных вызовов
        mock_get_rate.side_effect = [75.5, 85.2]

        result1 = get_exchange_rate_cached("USD", "RUB")
        result2 = get_exchange_rate_cached("EUR", "RUB")

        assert result1 == 75.5
        assert result2 == 85.2
        assert mock_get_rate.call_count == 2

        # Проверяем что оба значения закэшированы
        result3 = get_exchange_rate_cached("USD", "RUB")
        result4 = get_exchange_rate_cached("EUR", "RUB")

        assert result3 == 75.5
        assert result4 == 85.2
        assert mock_get_rate.call_count == 2  # Все еще 2 вызова

    @patch('src.external_api.get_exchange_rate')
    def test_get_exchange_rate_cached_none_result(self, mock_get_rate):
        """Тест кэширования когда API возвращает None."""
        # Первый вызов возвращает None
        mock_get_rate.return_value = None

        result1 = get_exchange_rate_cached("USD", "RUB")
        result2 = get_exchange_rate_cached("USD", "RUB")  # Должен снова вызвать API

        assert result1 is None
        assert result2 is None
        assert mock_get_rate.call_count == 2  # Два вызова, так как None не кэшируется

    @patch('src.external_api.get_exchange_rate')
    def test_get_exchange_rate_cached_mixed_results(self, mock_get_rate):
        """Тест кэширования с разными результатами."""
        # Первый вызов возвращает курс, второй - None
        mock_get_rate.side_effect = [75.5, None]

        result1 = get_exchange_rate_cached("USD", "RUB")  # Кэширует 75.5
        result2 = get_exchange_rate_cached("EUR", "RUB")  # Не кэширует None
        result3 = get_exchange_rate_cached("USD", "RUB")  # Должен вернуть из кэша

        assert result1 == 75.5
        assert result2 is None
        assert result3 == 75.5  # Из кэша
        assert mock_get_rate.call_count == 2  # USD (75.5) + EUR (None)