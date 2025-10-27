import pytest
import sys
import os
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils import load_json_data, setup_logger


class TestUtils:
    """Тесты для utils.py"""

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.path.getsize')
    def test_load_json_data_success(self, mock_getsize, mock_isfile, mock_exists):
        """Тест успешной загрузки JSON данных"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 100

        json_data = '[{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]'

        with patch('builtins.open', mock_open(read_data=json_data)):
            result = load_json_data("test.json")

        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['name'] == 'test2'

    @patch('os.path.exists')
    def test_load_json_data_file_not_found(self, mock_exists):
        """Тест загрузки несуществующего файла"""
        mock_exists.return_value = False

        result = load_json_data("nonexistent.json")

        assert result == []

    @patch('os.path.exists')
    @patch('os.path.isfile')
    def test_load_json_data_is_directory(self, mock_isfile, mock_exists):
        """Тест загрузки директории вместо файла"""
        mock_exists.return_value = True
        mock_isfile.return_value = False

        result = load_json_data("directory")

        assert result == []

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.path.getsize')
    def test_load_json_data_empty_file(self, mock_getsize, mock_isfile, mock_exists):
        """Тест загрузки пустого файла"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 0

        result = load_json_data("empty.json")

        assert result == []

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.path.getsize')
    def test_load_json_data_invalid_json(self, mock_getsize, mock_isfile, mock_exists):
        """Тест загрузки некорректного JSON"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 100

        with patch('builtins.open', mock_open(read_data='invalid json')):
            result = load_json_data("invalid.json")

        assert result == []

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.path.getsize')
    def test_load_json_data_not_list(self, mock_getsize, mock_isfile, mock_exists):
        """Тест загрузки JSON который не является списком"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 100

        json_data = '{"id": 1, "name": "test"}'

        with patch('builtins.open', mock_open(read_data=json_data)):
            result = load_json_data("object.json")

        assert result == []

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.path.getsize')
    def test_load_json_data_permission_error(self, mock_getsize, mock_isfile, mock_exists):
        """Тест ошибки прав доступа"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 100

        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = load_json_data("protected.json")

        assert result == []

    @patch('os.path.exists')
    @patch('os.path.isfile')
    @patch('os.path.getsize')
    def test_load_json_data_general_exception(self, mock_getsize, mock_isfile, mock_exists):
        """Тест общего исключения"""
        mock_exists.return_value = True
        mock_isfile.return_value = True
        mock_getsize.return_value = 100

        with patch('builtins.open', side_effect=Exception("Unexpected error")):
            result = load_json_data("error.json")

        assert result == []

    def test_load_json_data_edge_cases(self):
        """Тест граничных случаев загрузки JSON"""
        # Пустая строка
        result = load_json_data("")
        assert result == []

        # None
        result = load_json_data(None)
        assert result == []

    def test_setup_logger_new(self):
        """Тест создания нового логгера"""
        logger = setup_logger('test_utils')
        assert logger.name == 'test_utils'

    def test_setup_logger_existing(self):
        """Тест получения существующего логгера"""
        logger1 = setup_logger('existing_utils')
        logger2 = setup_logger('existing_utils')
        assert logger1 is logger2

    def test_setup_logger_force_recreate(self):
        """Тест принудительного пересоздания логгера"""
        logger1 = setup_logger('recreate_test')
        logger2 = setup_logger('recreate_test', force_recreate=True)
        # Проверяем что это тот же объект логгера
        assert logger1 is logger2
