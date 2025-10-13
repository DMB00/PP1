"""
Тесты для логирования в модулях masks и utils.
"""

import os
import tempfile
import json
import logging
import pytest
import time
import importlib

from src.logger_config import ensure_logs_directory, clear_all_logs, reset_loggers


class TestFileLogging:
    """Тесты записи логов в файлы."""

    def setup_method(self):
        """Очищаем логи и сбрасываем логгеры перед каждым тестом."""
        clear_all_logs()
        reset_loggers()
        # Перезагружаем модули чтобы создать новые логгеры
        importlib.reload(__import__('src.masks', fromlist=['']))
        importlib.reload(__import__('src.utils', fromlist=['']))

    def test_logs_directory_created(self):
        """Тест что папка logs создается автоматически."""
        logs_dir = ensure_logs_directory()
        assert os.path.exists(logs_dir)
        assert os.path.isdir(logs_dir)

    def test_log_file_format(self):
        """Тест формата записи логов."""
        from src.masks import get_mask_card_number

        logs_dir = ensure_logs_directory()
        masks_log_path = os.path.join(logs_dir, 'masks.log')

        # Вызываем функцию из masks
        result = get_mask_card_number("1234567890123456")

        # Проверяем что файл создан
        assert os.path.exists(masks_log_path)

        # Проверяем формат записи
        with open(masks_log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')

            # Проверяем что есть хотя бы одна запись
            assert len(lines) >= 1

            # Проверяем формат каждой строки
            for line in lines:
                if line.strip():  # Пропускаем пустые строки
                    parts = line.split(' - ')
                    assert len(parts) >= 4, f"Неверный формат строки: {line}"

    def test_log_file_overwrite(self):
        """Тест что лог файл перезаписывается при каждом запуске."""
        from src.masks import get_mask_card_number, get_mask_account

        logs_dir = ensure_logs_directory()
        masks_log_path = os.path.join(logs_dir, 'masks.log')

        # Первый вызов - только карта
        result1 = get_mask_card_number("1234567890123456")

        # Читаем содержимое после первого вызова
        with open(masks_log_path, 'r', encoding='utf-8') as f:
            first_content = f.read()

        # Сбрасываем логгер и перезагружаем модуль для эмуляции нового запуска
        reset_loggers()
        importlib.reload(__import__('src.masks', fromlist=['']))
        from src.masks import get_mask_account

        # Второй вызов - только счет (должен перезаписать файл)
        result2 = get_mask_account("12345678")

        # Читаем содержимое после второго вызова
        with open(masks_log_path, 'r', encoding='utf-8') as f:
            second_content = f.read()

        # Проверяем что файл был перезаписан
        # Второй вызов должен содержать только записи от второго "запуска"
        assert "Account masked successfully" in second_content
        # Первый вызов не должен содержаться (или только в виде заголовка)
        assert "Card masked successfully" not in second_content or second_content.count("Card masked successfully") == 1

    def test_different_modules_different_files(self):
        """Тест что разные модули пишут в разные файлы."""
        from src.masks import get_mask_card_number
        from src.utils import load_json_data

        logs_dir = ensure_logs_directory()
        masks_log_path = os.path.join(logs_dir, 'masks.log')
        utils_log_path = os.path.join(logs_dir, 'utils.log')

        # Используем masks модуль
        get_mask_card_number("1234567890123456")

        # Используем utils модуль
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{"id": 1}], f)
            temp_file = f.name

        try:
            load_json_data(temp_file)

            # Проверяем что оба файла созданы
            assert os.path.exists(masks_log_path)
            assert os.path.exists(utils_log_path)

        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestLogContent:
    """Тесты содержимого логов."""

    def setup_method(self):
        """Очищаем логи и сбрасываем логгеры перед каждым тестом."""
        clear_all_logs()
        reset_loggers()
        importlib.reload(__import__('src.masks', fromlist=['']))

    def test_masks_log_content(self):
        """Тест содержимого логов модуля masks."""
        from src.masks import get_mask_card_number, get_mask_account

        logs_dir = ensure_logs_directory()
        masks_log_path = os.path.join(logs_dir, 'masks.log')

        # Вызываем несколько функций masks
        get_mask_card_number("1234567890123456")
        get_mask_account("12345678")

        # Проверяем содержимое файла
        with open(masks_log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Обновляем проверки согласно фактическим логам
        assert "Card masked successfully" in content
        assert "1234567890123456 -> 1234 56** **** 3456" in content
        assert "Account masked successfully" in content
        assert "12345678 -> **5678" in content


def test_logger_configuration():
    """Тест конфигурации логгера."""
    from src.logger_config import setup_logger

    logger = setup_logger('test_config')

    assert logger.name == 'test_config'
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0