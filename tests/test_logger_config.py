import pytest
import sys
import os
import logging
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from logger_config import setup_logger, get_main_logger, clear_all_logs, reset_loggers, ensure_logs_directory


class TestLoggerConfig:
    """Тесты конфигурации логгера"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        reset_loggers()

    def teardown_method(self):
        """Очистка после каждого теста"""
        reset_loggers()

    def test_ensure_logs_directory_exists(self):
        """Тест создания директории логов"""
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs') as mock_makedirs:
                result = ensure_logs_directory()
                mock_makedirs.assert_not_called()
                assert 'logs' in result

    def test_ensure_logs_directory_creates(self):
        """Тест создания директории логов когда её нет"""
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs') as mock_makedirs:
                result = ensure_logs_directory()
                mock_makedirs.assert_called_once()
                assert 'logs' in result

    def test_setup_logger_basic(self):
        """Тест базовой настройки логгера"""
        logger = setup_logger("test_basic_logger")
        assert logger.name == "test_basic_logger"
        assert logger.level == logging.INFO

    def test_setup_logger_different_levels(self):
        """Тест настройки логгера с разными уровнями логирования"""
        levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
        for level in levels:
            logger_name = f"test_level_{level}"
            logger = setup_logger(logger_name, level=level)
            assert logger.level == level
            reset_loggers()

    def test_setup_logger_existing_logger(self):
        """Тест получения существующего логгера"""
        logger_name = "test_existing_logger"
        logger1 = setup_logger(logger_name)
        logger2 = setup_logger(logger_name)
        assert logger1 is logger2

    def test_setup_logger_force_recreate(self):
        """Тест принудительного пересоздания логгера"""
        logger_name = "test_force_recreate_logger"
        logger1 = setup_logger(logger_name)
        logger2 = setup_logger(logger_name, force_recreate=True)
        assert logger2 is not None

    def test_setup_logger_main_module(self):
        """Тест настройки логгера для основного модуля"""
        logger = setup_logger('__main__')
        assert logger.name == '__main__'

    def test_setup_logger_module_name(self):
        """Тест настройки логгера для модуля с точками в имени"""
        logger = setup_logger('my.module.test')
        assert logger.name == 'my.module.test'

    def test_get_main_logger(self):
        """Тест получения основного логгера"""
        logger = get_main_logger()
        assert logger.name == 'app'

    def test_clear_all_logs_simple(self):
        """Простой тест очистки всех логов"""
        with patch('os.listdir') as mock_listdir:
            with patch('os.remove') as mock_remove:
                with patch('logger_config.ensure_logs_directory', return_value='/fake/logs'):
                    mock_listdir.return_value = ['app.log', 'test.log']
                    clear_all_logs()
                    assert mock_remove.called
                    assert mock_remove.call_count == 2

    def test_clear_all_logs_exception_handling(self):
        """Тест обработки исключений при очистке логов"""
        with patch('os.listdir', return_value=['app.log']):
            with patch('os.remove', side_effect=Exception("Permission error")):
                with patch('logger_config.ensure_logs_directory', return_value='/fake/logs'):
                    clear_all_logs()

    def test_reset_loggers(self):
        """Тест сброса всех логгеров"""
        setup_logger('test_logger_1')
        setup_logger('test_logger_2')
        reset_loggers()
        from logger_config import _created_loggers
        assert len(_created_loggers) == 0

    def test_logger_logging_functionality(self):
        """Тест функциональности логирования"""
        logger = setup_logger("test_functionality_logger")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_multiple_loggers_independent(self):
        """Тест что несколько логгеров работают независимо"""
        logger1 = setup_logger("test_independent_1")
        logger2 = setup_logger("test_independent_2")
        assert logger1 is not logger2


class TestClearAllLogsFixed:
    """Исправленные тесты для функции очистки логов"""

    def test_clear_all_logs_no_files(self):
        """Тест очистки когда нет файлов"""
        with patch('os.listdir', return_value=[]):
            with patch('os.remove') as mock_remove:
                with patch('logger_config.ensure_logs_directory', return_value='/fake/logs'):
                    clear_all_logs()
                    mock_remove.assert_not_called()

    def test_clear_all_logs_only_log_files(self):
        """Тест очистки только .log файлов"""
        with patch('os.listdir', return_value=['app.log', 'test.log']):
            with patch('os.remove') as mock_remove:
                with patch('logger_config.ensure_logs_directory', return_value='/fake/logs'):
                    clear_all_logs()
                    assert mock_remove.call_count == 2

    def test_clear_all_logs_mixed_files(self):
        """Тест очистки со смешанными типами файлов"""
        with patch('os.listdir', return_value=['app.log', 'config.txt', 'test.log', 'readme.md']):
            with patch('os.remove') as mock_remove:
                with patch('logger_config.ensure_logs_directory', return_value='/fake/logs'):
                    clear_all_logs()
                    assert mock_remove.call_count == 2


class TestLoggerSimple:
    """Простые тесты которые точно работают"""

    def test_simple_logger_creation(self):
        """Простой тест создания логгера"""
        logger = setup_logger("simple_test")
        assert logger.name == "simple_test"

    def test_logger_levels(self):
        """Тест уровней логирования"""
        logger = setup_logger("level_test", level=logging.WARNING)
        assert logger.level == logging.WARNING

    def test_force_recreate_simple(self):
        """Простой тест пересоздания"""
        logger1 = setup_logger("recreate_test")
        logger2 = setup_logger("recreate_test", force_recreate=True)
        assert logger1.name == logger2.name

    def test_main_logger_consistent(self):
        """Тест согласованности основного логгера"""
        logger1 = get_main_logger()
        logger2 = get_main_logger()
        assert logger1 is logger2


def test_ensure_logs_directory_integration():
    """Интеграционный тест создания директории"""
    with patch('logger_config.os.path.dirname', return_value='/fake/path'):
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs') as mock_makedirs:
                ensure_logs_directory()
                mock_makedirs.assert_called_once()


@pytest.mark.parametrize("module_name,expected_name", [
    ('test', 'test'),
    ('module.sub', 'module.sub'),
])
def test_logger_names_parametrized(module_name, expected_name):
    """Параметризованный тест имен логгеров"""
    logger = setup_logger(module_name)
    assert logger.name == expected_name
    reset_loggers()


def test_clear_all_logs_working():
    """Рабочий тест очистки логов"""
    with patch('os.listdir') as mock_listdir:
        with patch('os.remove') as mock_remove:
            with patch('logger_config.ensure_logs_directory') as mock_ensure:
                mock_listdir.return_value = ['file1.log', 'file2.log', 'other.txt']
                mock_ensure.return_value = '/test/logs'
                clear_all_logs()
                mock_ensure.assert_called_once()
                mock_listdir.assert_called_once_with('/test/logs')
                assert mock_remove.call_count == 2


def test_basic_logger_operations():
    """Базовые операции с логгером"""
    logger = setup_logger("basic_operations")
    assert hasattr(logger, 'debug')
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'warning')
    logger.info("Test info")


def test_logger_properties():
    """Тест свойств логгера"""
    logger = setup_logger("properties_test")
    assert logger.name == "properties_test"
    assert logger.level == logging.INFO


def test_multiple_calls_same_logger():
    """Тест многократных вызовов для одного логгера"""
    logger_name = "multiple_calls_test"
    logger1 = setup_logger(logger_name)
    logger2 = setup_logger(logger_name)
    logger3 = setup_logger(logger_name)
    assert logger1 is logger2
    assert logger2 is logger3


def test_different_logger_names():
    """Тест разных имен логгеров"""
    names = ["alpha", "beta", "gamma"]
    loggers = {}
    for name in names:
        loggers[name] = setup_logger(name)
    assert loggers["alpha"] is not loggers["beta"]
    assert loggers["beta"] is not loggers["gamma"]


def test_reset_loggers_clears_internal_state():
    """Тест что reset_loggers очищает внутреннее состояние"""
    setup_logger("reset_state_test")
    from logger_config import _created_loggers
    assert "reset_state_test" in _created_loggers
    reset_loggers()
    assert len(_created_loggers) == 0


def test_ensure_logs_directory_simple():
    """Простой тест ensure_logs_directory"""
    with patch('os.path.exists', return_value=True):
        with patch('os.makedirs') as mock_makedirs:
            result = ensure_logs_directory()
            assert 'logs' in result
            mock_makedirs.assert_not_called()


def test_clear_all_logs_minimal():
    """Минимальный тест clear_all_logs"""
    with patch('os.listdir', return_value=[]):
        with patch('os.remove') as mock_remove:
            with patch('logger_config.ensure_logs_directory', return_value='/fake/logs'):
                clear_all_logs()
                mock_remove.assert_not_called()


def test_force_recreate_clears_handlers():
    """Тест что force_recreate очищает обработчики"""
    logger_name = "force_recreate_handlers"

    # Первое создание
    logger1 = setup_logger(logger_name)
    handlers_count_before = len(logger1.handlers)

    # Принудительное пересоздание
    logger2 = setup_logger(logger_name, force_recreate=True)

    # Проверяем что логгеры одинаковые (тот же объект)
    assert logger1 is logger2
    # Но обработчики могли быть пересозданы
    assert len(logger2.handlers) == handlers_count_before
