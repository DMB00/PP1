"""
Модуль utils содержит вспомогательные функции для работы с данными.
"""

import json
import os
from typing import List, Dict, Any


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные из JSON-файла и возвращает список словарей с транзакциями.

    Args:
        file_path: путь до JSON-файла

    Returns:
        List[Dict[str, Any]]: список словарей с данными о транзакциях
        или пустой список, если файл не найден, пустой или содержит не список
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            return []

        # Проверяем что это файл, а не директория
        if not os.path.isfile(file_path):
            return []

        # Проверяем что файл не пустой
        if os.path.getsize(file_path) == 0:
            return []

        # Читаем и парсим JSON файл
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем что данные - это список
        if not isinstance(data, list):
            return []

        return data

    except json.JSONDecodeError:
        # Ошибка декодирования JSON
        return []
    except PermissionError:
        # Нет прав доступа к файлу
        return []
    except Exception:
        # Любая другая ошибка
        return []
