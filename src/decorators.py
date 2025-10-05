"""
Модуль decorators содержит полезные декораторы для проекта.
"""

from datetime import datetime
import functools
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования начала и конца выполнения функции.

    Args:
        filename: Имя файла для записи логов. Если None, логи выводятся в консоль.

    Returns:
        Декоратор функции
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Получаем текущее время для лога
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            func_name = func.__name__

            # Формируем строку с аргументами
            args_str = ", ".join([repr(arg) for arg in args])
            kwargs_str = ", ".join([f"{key}={repr(value)}" for key, value in kwargs.items()])
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))

            # Логируем начало выполнения функции
            start_message = f"{current_time} - {func_name}({all_args}) - начало выполнения"

            def write_log(message: str) -> None:
                """Вспомогательная функция для записи лога."""
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(message + "\n")
                else:
                    print(message)

            write_log(start_message)

            try:
                # Выполняем функцию
                result = func(*args, **kwargs)

                # Логируем успешное завершение
                success_message = f"{current_time} - {func_name}({all_args}) - успешно завершено -> {repr(result)}"
                write_log(success_message)

                return result

            except Exception as e:
                # Логируем ошибку
                error_message = (f"{current_time} - {func_name}({all_args}) - "
                                 f"вызвано исключение {type(e).__name__}: {str(e)}")
                write_log(error_message)

                # Пробрасываем исключение дальше
                raise

        return wrapper

    return decorator


# Дополнительные декораторы для демонстрации
def timer(func: Callable) -> Callable:
    """
    Декоратор для измерения времени выполнения функции.
    """
    import functools
    import time

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"Функция {func.__name__} выполнена за {execution_time:.4f} секунд")

        return result

    return wrapper


def validate_currency(func: Callable) -> Callable:
    """
    Декоратор для валидации валюты в функциях работы с транзакциями.
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        currency = None

        # Ищем currency в аргументах
        if len(args) >= 2:
            currency = args[1]
        elif 'currency' in kwargs:
            currency = kwargs['currency']

        # Валидация
        if currency and not isinstance(currency, str):
            raise TypeError("Валюта должна быть строкой")

        if currency and len(currency) != 3:
            raise ValueError("Код валюты должен состоять из 3 символов")

        return func(*args, **kwargs)

    return wrapper


from datetime import datetime
from functools import wraps


def log(filename: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if filename:
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp} - {func_name} - вызвана\n")
            else:
                print(f"{timestamp} - {func_name} - вызвана")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def cache(func):
    """
    Декоратор для кэширования результатов функции.
    """
    cache_dict = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Создаем ключ на основе аргументов
        key = (args, tuple(sorted(kwargs.items())))

        if key not in cache_dict:
            cache_dict[key] = func(*args, **kwargs)

        return cache_dict[key]

    # Добавляем метод для очистки кэша
    wrapper.cache_clear = lambda: cache_dict.clear()

    return wrapper
