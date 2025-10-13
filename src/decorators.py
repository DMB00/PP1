"""
Модуль decorators содержит декораторы для функций.
"""

from datetime import datetime
from functools import wraps


def log(filename: str = None):
    """Декоратор для логирования вызовов функций."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Логируем вызов
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"{timestamp} - {func.__name__} - вызвана"

            if filename:
                with open(filename, "a", encoding="utf-8") as f:
                    f.write(message + "\n")
            else:
                print(message)

            # Вызываем функцию
            return func(*args, **kwargs)

        return wrapper

    return decorator


def cache(func):
    """Декоратор для кэширования результатов."""
    cache_dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Создаем ключ для кэша
        key = str(args) + str(sorted(kwargs.items()))

        if key not in cache_dict:
            cache_dict[key] = func(*args, **kwargs)

        return cache_dict[key]

    # Метод для очистки кэша
    wrapper.cache_clear = lambda: cache_dict.clear()

    return wrapper