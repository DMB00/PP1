import pytest
import logging
from unittest.mock import patch, MagicMock
from src.logger_config import setup_logger, clear_all_logs, reset_loggers, ensure_logs_directory, _created_loggers


class TestLoggerConfig:
    """Тесты для конфигурации логгера"""

    def setup_method(self):
        reset_loggers()

    def teardown_method(self):
        reset_loggers()

    def test_setup_logger_basic(self):
        """Базовый тест создания логгера"""
        with patch('src.logger_config.logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            with patch('src.logger_config.logging.StreamHandler'):
                with patch('src.logger_config.logging.FileHandler'):
                    with patch('src.logger_config.logging.Formatter'):
                        with patch('src.logger_config.ensure_logs_directory'):
                            with patch('src.logger_config.sys.stdout'):
                                logger = setup_logger('test')

                                assert logger is mock_logger
                                mock_logger.setLevel.assert_called_with(logging.INFO)

    def test_reset_loggers(self):
        """Тест сброса логгеров"""
        _created_loggers.add('test1')
        _created_loggers.add('test2')
        reset_loggers()
        assert len(_created_loggers) == 0

    def test_clear_all_logs_basic(self):
        """Простой тест очистки логов"""
        with patch('src.logger_config.ensure_logs_directory') as mock_ensure:
            with patch('src.logger_config.os.listdir') as mock_listdir:
                with patch('src.logger_config.os.remove') as mock_remove:
                    mock_ensure.return_value = '/logs'
                    mock_listdir.return_value = ['app.log', 'test.log']

                    clear_all_logs()

                    # Просто проверяем что remove вызывался 2 раза
                    assert mock_remove.call_count == 2

    def test_clear_all_logs_no_files(self):
        """Тест очистки когда нет файлов"""
        with patch('src.logger_config.ensure_logs_directory') as mock_ensure:
            with patch('src.logger_config.os.listdir') as mock_listdir:
                with patch('src.logger_config.os.remove') as mock_remove:
                    mock_ensure.return_value = '/logs'
                    mock_listdir.return_value = []

                    clear_all_logs()

                    mock_remove.assert_not_called()

    def test_ensure_logs_directory_creates(self):
        """Тест создания директории"""
        with patch('src.logger_config.os.path.exists') as mock_exists:
            with patch('src.logger_config.os.makedirs') as mock_makedirs:
                mock_exists.return_value = False

                result = ensure_logs_directory()

                mock_makedirs.assert_called_once()
                assert 'logs' in result

    def test_ensure_logs_directory_exists(self):
        """Тест когда директория существует"""
        with patch('src.logger_config.os.path.exists') as mock_exists:
            with patch('src.logger_config.os.makedirs') as mock_makedirs:
                mock_exists.return_value = True

                result = ensure_logs_directory()

                mock_makedirs.assert_not_called()
                assert 'logs' in result


def test_setup_logger_adds_to_created_set():
    """Тест что логгер добавляется в множество"""
    with patch('src.logger_config.logging.getLogger'):
        with patch('src.logger_config.logging.StreamHandler'):
            with patch('src.logger_config.logging.FileHandler'):
                with patch('src.logger_config.logging.Formatter'):
                    with patch('src.logger_config.ensure_logs_directory'):
                        with patch('src.logger_config.sys.stdout'):
                            reset_loggers()
                            setup_logger('test')
                            assert 'test' in _created_loggers


def test_multiple_loggers_same_instance():
    """Тест что multiple calls return same instance"""
    with patch('src.logger_config.logging.getLogger') as mock_get_logger:
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        with patch('src.logger_config.logging.StreamHandler'):
            with patch('src.logger_config.logging.FileHandler'):
                with patch('src.logger_config.logging.Formatter'):
                    with patch('src.logger_config.ensure_logs_directory'):
                        with patch('src.logger_config.sys.stdout'):
                            logger1 = setup_logger('test')
                            logger2 = setup_logger('test')
                            assert logger1 is logger2


def test_clear_all_logs_only_removes_log_files():
    """Тест что удаляются только .log файлы"""
    with patch('src.logger_config.ensure_logs_directory') as mock_ensure:
        with patch('src.logger_config.os.listdir') as mock_listdir:
            with patch('src.logger_config.os.remove') as mock_remove:
                mock_ensure.return_value = '/logs'
                mock_listdir.return_value = ['app.log', 'test.txt', 'config.ini', 'error.log']

                clear_all_logs()

                # Должны быть удалены только .log файлы
                assert mock_remove.call_count == 2
                # Проверяем что в вызовах есть .log файлы
                all_calls = str(mock_remove.call_args_list)
                assert 'app.log' in all_calls
                assert 'error.log' in all_calls
                assert 'test.txt' not in all_calls


def test_file_handler_created_with_correct_path():
    """Тест что FileHandler создается с правильным путем"""
    with patch('src.logger_config.logging.getLogger'):
        with patch('src.logger_config.logging.StreamHandler'):
            with patch('src.logger_config.logging.FileHandler') as mock_file_handler:
                with patch('src.logger_config.logging.Formatter'):
                    with patch('src.logger_config.ensure_logs_directory') as mock_ensure:
                        with patch('src.logger_config.sys.stdout'):
                            mock_ensure.return_value = '/logs'

                            setup_logger('test_module')

                            # Проверяем что FileHandler был вызван
                            assert mock_file_handler.called
                            # Проверяем что путь содержит ожидаемое имя файла
                            call_args = str(mock_file_handler.call_args)
                            assert 'test_module.log' in call_args


@pytest.mark.parametrize("logger_name,expected_file", [
    ('simple', 'simple.log'),
    ('main', 'main.log'),
    ('__main__', 'app.log'),
])
def test_different_logger_names(logger_name, expected_file):
    """Тест разных имен логгеров"""
    with patch('src.logger_config.logging.getLogger'):
        with patch('src.logger_config.logging.StreamHandler'):
            with patch('src.logger_config.logging.FileHandler') as mock_file_handler:
                with patch('src.logger_config.logging.Formatter'):
                    with patch('src.logger_config.ensure_logs_directory'):
                        with patch('src.logger_config.sys.stdout'):
                            setup_logger(logger_name)

                            call_args = str(mock_file_handler.call_args)
                            assert expected_file in call_args
