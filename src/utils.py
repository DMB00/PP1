import json
import os
from typing import List, Dict, Any
from .logger_config import setup_logger

# Создаем логгер для модуля utils с принудительным пересозданием
logger = setup_logger('utils', force_recreate=True)


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные из JSON-файла.
    """
    logger.debug(f"Starting JSON data loading from: {file_path}")

    try:
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return []

        if not os.path.isfile(file_path):
            logger.warning(f"Path is directory, not file: {file_path}")
            return []

        if os.path.getsize(file_path) == 0:
            logger.warning(f"File is empty: {file_path}")
            return []

        logger.debug(f"Reading file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if not isinstance(data, list):
            logger.warning(f"File {file_path} contains {type(data).__name__}, not list")
            return []

        logger.info(f"Successfully loaded {len(data)} records from {file_path}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in file {file_path}: {e}")
        return []
    except PermissionError as e:
        logger.error(f"Permission error for file {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error reading file {file_path}: {e}")
        return []
