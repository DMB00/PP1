"""
Конфигурация логгера
"""

import logging
import sys
import os
from datetime import datetime

# Глобальный словарь для отслеживания созданных логгеров
_created_loggers = set()


def ensure_logs_directory():
    """
    Создает папку logs, если она не существует.
    """
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    return logs_dir


def setup_logger(name: str, level: int = logging.INFO, force_recreate: bool = False) -> logging.Logger:
    """
    Настраивает и возвращает логгер.

    Args:
        name: имя логгера (обычно __name__ модуля)
        level: уровень логирования
        force_recreate: принудительно пересоздать логгер

    Returns:
        logging.Logger: настроенный логгер
    """
    # Получаем или создаем логгер
    logger = logging.getLogger(name)

    # Если force_recreate=True или логгер еще не настраивался, настраиваем его
    if force_recreate or name not in _created_loggers:
        # Удаляем существующие обработчики
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        logger.setLevel(level)

        # Форматтер для логов (метка времени, модуль, уровень, сообщение)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Обработчик для консоли
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Создаем папку для логов
        logs_dir = ensure_logs_directory()

        # Определяем имя файла лога на основе имени модуля
        if name == '__main__':
            log_file_name = 'app.log'
        else:
            # Преобразуем имя модуля в имя файла
            module_name = name.split('.')[-1] if '.' in name else name
            log_file_name = f'{module_name}.log'

        log_file_path = os.path.join(logs_dir, log_file_name)

        # Обработчик для файла с перезаписью при каждом запуске ('w' mode)
        file_handler = logging.FileHandler(
            log_file_path,
            mode='w',  # Перезаписываем файл при каждом запуске
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Добавляем обработчики к логгеру
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Записываем заголовок запуска
        logger.info(f"=== Запуск приложения {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

        # Помечаем логгер как настроенный
        _created_loggers.add(name)

    return logger


def get_main_logger() -> logging.Logger:
    """
    Возвращает основной логгер для приложения.

    Returns:
        logging.Logger: основной логгер
    """
    return setup_logger('app')


def clear_all_logs():
    """
    Полностью удаляет все файлы логов.
    Используется для тестов.
    """
    logs_dir = ensure_logs_directory()
    for file_name in os.listdir(logs_dir):
        if file_name.endswith('.log'):
            file_path = os.path.join(logs_dir, file_name)
            try:
                os.remove(file_path)
            except Exception:
                pass


def reset_loggers():
    """
    Сбрасывает все созданные логгеры.
    Используется в тестах для принудительного пересоздания.
    """
    global _created_loggers
    _created_loggers.clear()

    # Получаем корневой логгер и сбрасываем его обработчики
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
