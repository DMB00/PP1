# src/bank_search.py
import re
from typing import List, Dict
import logging


# Создаем простой логгер
def setup_logger(name, force_recreate=False):
    """Создает простой логгер"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = setup_logger('bank_search', force_recreate=True)


def process_bank_search(data: List[Dict], search: str) -> List[Dict]:
    """
    Фильтрует список банковских операций по строке поиска в описании.
    """
    logger.info(f"Starting bank search with query: '{search}'")

    # Обработка None и невалидных входных данных
    if data is None:
        logger.warning("None data provided")
        return []

    if not data:
        logger.warning("Empty data list provided")
        return []

    if search is None:
        logger.warning("None search query provided")
        return []

    search = search.strip()
    if not search:
        logger.warning("Empty search query provided")
        return data

    try:
        # Создаем регулярное выражение для поиска
        pattern = re.compile(re.escape(search), re.IGNORECASE)
        logger.debug(f"Compiled regex pattern: {pattern.pattern}")

        filtered_data = []

        for operation in data:
            # Проверяем наличие поля 'description' и ищем в нем
            if operation.get('description'):
                description = str(operation['description'])

                # Ищем совпадение с помощью регулярного выражения
                if pattern.search(description):
                    filtered_data.append(operation)

        logger.info(f"Search completed. Found {len(filtered_data)} matching operations")
        return filtered_data

    except re.error as e:
        logger.error(f"Regex error with pattern '{search}': {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error during bank search: {e}")
        return []


def process_bank_operations(data: List[Dict], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество операций по категориям.
    """
    logger.info(f"Starting bank operations processing for categories: {categories}")

    # Обработка невалидных входных данных
    if data is None:
        logger.warning("None data provided")
        return {}

    if categories is None:
        logger.warning("None categories provided")
        return {}

    if not categories:
        logger.warning("Empty categories list provided")
        return {}

    if not data:
        logger.warning("Empty data list provided")
        return {category: 0 for category in categories}

    try:
        # Создаем словарь для подсчета с нулевыми значениями для всех категорий
        category_count = {category: 0 for category in categories}
        logger.debug(f"Initialized category count: {category_count}")

        # Подсчитываем операции по категориям
        operations_processed = 0
        operations_with_description = 0

        for operation in data:
            operations_processed += 1

            # Проверяем наличие описания
            if not operation.get('description'):
                continue

            operations_with_description += 1
            description = str(operation['description']).lower()

            # Проверяем каждую категорию
            for category in categories:
                category_lower = category.lower()
                # Простой поиск подстроки (без границ слов)
                if category_lower in description:
                    category_count[category] += 1

        logger.info(f"Processing completed. Processed {operations_processed} operations, "
                    f"{operations_with_description} with descriptions")
        logger.info(f"Category counts: {category_count}")

        return category_count

    except Exception as e:
        logger.error(f"Unexpected error during bank operations processing: {e}")
        return {category: 0 for category in categories} if categories else {}
