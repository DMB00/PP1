import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from external_api import (
    get_exchange_rate,
    convert_amount_to_rub,
    get_exchange_rate_cached,
    clear_exchange_rate_cache,
    get_api_status
)


class TestExternalAPI:
    """Тесты для external_api.py"""

    @patch('external_api.requests.get')
    @patch('external_api.os.getenv')
    def test_get_exchange_rate_success(self, mock_getenv, mock_get):
        """Тест успешного получения курса валют"""
        mock_getenv.return_value = "test_api_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 75.5}
        mock_get.return_value = mock_response

        result = get_exchange_rate("USD", "RUB")

        assert result == 75.5
        mock_get.assert_called_once()

    @patch('external_api.os.getenv')
    def test_get_exchange_rate_no_api_key(self, mock_getenv):
        """Тест отсутствия API ключа"""
        mock_getenv.return_value = None

        result = get_exchange_rate("USD", "RUB")

        assert result is None

    @patch('external_api.os.getenv')
    def test_get_exchange_rate_same_currency(self, mock_getenv):
        """Тест одинаковых валют"""
        mock_getenv.return_value = "test_key"

        result = get_exchange_rate("USD", "USD")

        assert result == 1.0

    @patch('external_api.requests.get')
    @patch('external_api.os.getenv')
    def test_get_exchange_rate_api_error(self, mock_getenv, mock_get):
        """Тест ошибки API"""
        mock_getenv.return_value = "test_key"
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response

        result = get_exchange_rate("USD", "RUB")

        assert result is None

    @patch('external_api.requests.get')
    @patch('external_api.os.getenv')
    def test_get_exchange_rate_request_exception(self, mock_getenv, mock_get):
        """Тест исключения RequestException"""
        mock_getenv.return_value = "test_key"
        mock_get.side_effect = Exception("Any exception")

        result = get_exchange_rate("USD", "RUB")
        assert result is None

    def test_convert_amount_to_rub_rub(self):
        """Тест конвертации RUB в RUB"""
        transaction = {
            "operationAmount": {
                "amount": "100.0",
                "currency": {"code": "RUB"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 100.0

    @patch('external_api.get_exchange_rate')
    def test_convert_amount_to_rub_usd(self, mock_get_rate):
        """Тест конвертации USD в RUB"""
        mock_get_rate.return_value = 75.0
        transaction = {
            "operationAmount": {
                "amount": "10.0",
                "currency": {"code": "USD"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 750.0

    def test_convert_amount_to_rub_unsupported_currency(self):
        """Тест конвертации неподдерживаемой валюты"""
        transaction = {
            "operationAmount": {
                "amount": "100.0",
                "currency": {"code": "GBP"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 100.0

    def test_convert_amount_to_rub_invalid_amount(self):
        """Тест конвертации с невалидной суммой"""
        transaction = {
            "operationAmount": {
                "amount": "invalid",
                "currency": {"code": "USD"}
            }
        }

        result = convert_amount_to_rub(transaction)
        assert result == 0.0

    def test_convert_amount_to_rub_missing_data(self):
        """Тест конвертации с отсутствующими данными"""
        result = convert_amount_to_rub({})
        assert result == 0.0

        result = convert_amount_to_rub(None)
        assert result == 0.0

    def test_convert_amount_to_rub_missing_operation_amount(self):
        """Тест конвертации без operationAmount"""
        transaction = {"other_field": "value"}
        result = convert_amount_to_rub(transaction)
        assert result == 0.0

    @patch('external_api.get_exchange_rate')
    def test_get_exchange_rate_cached(self, mock_get_rate):
        """Тест кэширования курса валют"""
        mock_get_rate.return_value = 75.0

        # Очищаем кэш перед тестом
        clear_exchange_rate_cache()

        # Первый вызов
        result1 = get_exchange_rate_cached("USD", "RUB")

        # Второй вызов
        result2 = get_exchange_rate_cached("USD", "RUB")

        assert result1 == 75.0
        assert result2 == 75.0
        mock_get_rate.assert_called_once()

    def test_clear_exchange_rate_cache(self):
        """Тест очистки кэша"""
        # Добавляем данные в кэш
        from external_api import _exchange_rate_cache
        _exchange_rate_cache["USD_RUB"] = 75.0

        clear_exchange_rate_cache()

        assert _exchange_rate_cache == {}

    @patch('external_api.requests.get')
    @patch('external_api.os.getenv')
    def test_get_api_status_success(self, mock_getenv, mock_get):
        """Тест успешной проверки статуса API"""
        mock_getenv.return_value = "test_key"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = get_api_status()
        assert result is True

    @patch('external_api.requests.get')
    @patch('external_api.os.getenv')
    def test_get_api_status_failure(self, mock_getenv, mock_get):
        """Тест неудачной проверки статуса API"""
        mock_getenv.return_value = "test_key"
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = get_api_status()
        assert result is False

    @patch('external_api.os.getenv')
    def test_get_api_status_no_key(self, mock_getenv):
        """Тест проверки статуса без API ключа"""
        mock_getenv.return_value = None

        result = get_api_status()
        assert result is False

    @patch('external_api.requests.get')
    @patch('external_api.os.getenv')
    def test_get_api_status_general_exception(self, mock_getenv, mock_get):
        """Тест общего исключения при проверке статуса API"""
        mock_getenv.return_value = "test_key"
        mock_get.side_effect = MemoryError("Memory error")

        result = get_api_status()
        assert result is False
