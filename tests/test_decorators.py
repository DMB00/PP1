"""
Тесты для модуля decorators.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock


class TestLogDecorator:
    """Тесты для декоратора log."""

    def test_log_basic_functionality(self, capsys):
        """Тест базовой функциональности декоратора log."""
        from src.decorators import log

        @log()
        def simple_function(x):
            return x * 2

        result = simple_function(5)
        assert result == 10

        captured = capsys.readouterr()
        console_output = captured.out

        # Проверяем что есть вывод
        assert console_output.strip() != ""
        # Проверяем что вывод содержит элементы лога
        assert any(char in console_output for char in ['-', ':'])

    def test_log_with_file(self):
        """Тест логирования в файл."""
        from src.decorators import log

        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            log_filename = f.name

        try:
            @log(filename=log_filename)
            def file_function(x, y):
                return x + y

            result = file_function(3, 4)
            assert result == 7

            with open(log_filename, 'r', encoding='utf-8') as log_file:
                log_content = log_file.read()

            assert log_content.strip() != ""
            assert any(char in log_content for char in ['-', ':'])

        finally:
            if os.path.exists(log_filename):
                os.unlink(log_filename)

    def test_log_preserves_metadata(self):
        """Тест сохранения метаданных функции."""
        from src.decorators import log

        @log()
        def meta_function(x: int) -> str:
            """Test function documentation."""
            return str(x)

        # Проверяем что метаданные сохранились
        assert meta_function.__name__ == "meta_function"
        assert meta_function.__doc__ == "Test function documentation."
        assert meta_function.__annotations__ == {'x': int, 'return': str}


class TestCacheDecorator:
    """Тесты для декоратора cache."""

    def test_cache_basic_functionality(self):
        """Тест базовой функциональности кэширования."""
        from src.decorators import cache

        call_count = 0

        @cache
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Первый вызов - должен вычислить
        result1 = expensive_operation(5)
        assert result1 == 10
        assert call_count == 1

        # Второй вызов с теми же аргументами - должен вернуть из кэша
        result2 = expensive_operation(5)
        assert result2 == 10
        assert call_count == 1  # Не должно увеличиться

        # Вызов с другими аргументами - должен вычислить
        result3 = expensive_operation(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_different_arguments(self):
        """Тест кэширования с разными аргументами."""
        from src.decorators import cache

        @cache
        def multiply(x, y):
            return x * y

        assert multiply(2, 3) == 6
        assert multiply(2, 4) == 8
        assert multiply(2, 3) == 6  # Должен вернуть из кэша

    def test_cache_with_kwargs(self):
        """Тест кэширования с именованными аргументами."""
        from src.decorators import cache

        @cache
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result1 = greet("Alice")
        result2 = greet("Alice", greeting="Hi")
        result3 = greet("Alice")

        assert result1 == "Hello, Alice!"
        assert result2 == "Hi, Alice!"
        assert result3 == "Hello, Alice!"  # Из кэша

    def test_cache_clear_functionality(self):
        """Тест очистки кэша."""
        from src.decorators import cache

        call_count = 0

        @cache
        def counter():
            nonlocal call_count
            call_count += 1
            return call_count

        assert counter() == 1
        assert counter() == 1  # Из кэша

        # Очищаем кэш
        counter.cache_clear()

        assert counter() == 2  # Снова вычисляем
        assert counter() == 2  # Из кэша

    def test_cache_preserves_metadata(self):
        """Тест сохранения метаданных функции."""
        from src.decorators import cache

        @cache
        def cached_function(x: int) -> int:
            """Cached function documentation."""
            return x * 2

        # Проверяем что метаданные сохранились
        assert cached_function.__name__ == "cached_function"
        assert cached_function.__doc__ == "Cached function documentation."
        assert cached_function.__annotations__ == {'x': int, 'return': int}


def test_log_with_exception(capsys):
    """Тест логирования при исключениях."""
    from src.decorators import log

    @log()
    def error_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError):
        error_function()

    captured = capsys.readouterr()
    console_output = captured.out

    assert console_output.strip() != ""
    assert any(char in console_output for char in ['-', ':'])


def test_log_multiple_calls(capsys):
    """Тест множественных вызовов с логированием."""
    from src.decorators import log

    @log()
    def multi_call_function(x):
        return x + 1

    results = [multi_call_function(i) for i in range(3)]
    assert results == [1, 2, 3]

    captured = capsys.readouterr()
    console_output = captured.out

    assert console_output.strip() != ""
    assert any(char in console_output for char in ['-', ':'])
