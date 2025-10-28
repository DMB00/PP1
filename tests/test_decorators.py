import pytest
import sys
import os
from unittest.mock import patch, mock_open
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from decorators import log, cache


class TestDecorators:
    """Тесты для decorators.py"""

    def test_log_decorator_without_file(self):
        """Тест декоратора log без файла"""

        @log()
        def test_function():
            return "test_result"

        with patch('builtins.print') as mock_print:
            result = test_function()

            assert result == "test_result"
            assert mock_print.called

    def test_log_decorator_with_file(self):
        """Тест декоратора log с файлом"""

        @log(filename="test.log")
        def test_function():
            return "test_result"

        with patch('builtins.open', mock_open()) as mock_file:
            with patch('decorators.datetime') as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "2023-01-01 12:00:00"
                result = test_function()

            assert result == "test_result"
            assert mock_file.called

    def test_cache_decorator(self):
        """Тест декоратора cache"""
        call_count = 0

        @cache
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов
        result1 = test_function(5)
        assert result1 == 10
        assert call_count == 1

        # Второй вызов с теми же аргументами - должен быть из кэша
        result2 = test_function(5)
        assert result2 == 10
        assert call_count == 1  # Не увеличилось

        # Вызов с другими аргументами
        result3 = test_function(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_clear(self):
        """Тест очистки кэша"""
        call_count = 0

        @cache
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов
        test_function(5)
        assert call_count == 1

        # Второй вызов - из кэша
        test_function(5)
        assert call_count == 1

        # Очищаем кэш
        test_function.cache_clear()

        # Снова вызываем - должен посчитать заново
        test_function(5)
        assert call_count == 2

    def test_cache_with_kwargs(self):
        """Тест кэширования с keyword arguments"""

        @cache
        def test_function(a, b=0):
            return a + b

        result1 = test_function(5, b=3)
        result2 = test_function(5, b=3)

        assert result1 == 8
        assert result2 == 8

    def test_cache_different_kwargs_order(self):
        """Тест кэширования с разным порядком kwargs"""

        @cache
        def test_function(a, b=0, c=0):
            return a + b + c

        result1 = test_function(5, b=3, c=2)
        result2 = test_function(5, c=2, b=3)  # Другой порядок

        assert result1 == 10
        assert result2 == 10
