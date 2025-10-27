import sys
import os
import pytest
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import setup_logging


def test_setup_logging_basic():
    """Базовый тест настройки логирования"""
    # Просто проверяем что функция выполняется без ошибок
    try:
        setup_logging()
        # Проверяем что логгер можно использовать
        logger = logging.getLogger('test')
        logger.info("Test message")
        assert True
    except Exception as e:
        pytest.fail(f"setup_logging failed: {e}")


def test_logger_creation():
    """Тест создания логгера"""
    setup_logging()
    logger = logging.getLogger('test_logger')

    # Проверяем базовые свойства
    assert logger is not None
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'warning')
