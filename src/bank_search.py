import re
import logging
from collections import Counter
from typing import List, Dict, Any


def your_problem_method(self, input_data):
    """Метод который падает с TypeError"""
    # Добавляем проверку типа
    if not isinstance(input_data, (str, bytes)):
        if input_data is None:
            input_data = ""
        else:
            input_data = str(input_data)  # конвертируем в строку

def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """
    Поиск операций по строке в описании с использованием регулярных выражений
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Поиск операций по строке: '{search}'")

    if not data:
        return []

    if not search:
        return data

    try:
        pattern = re.compile(re.escape(search), re.IGNORECASE)
        filtered_operations = []

        for operation in data:
            description = operation.get('description', '')
            if pattern.search(description):
                filtered_operations.append(operation)

        logger.info(f"Найдено {len(filtered_operations)} операций по запросу '{search}'")
        return filtered_operations

    except re.error as e:
        logger.error(f"Ошибка в регулярном выражении '{search}': {e}")
        return []


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчет операций по категориям с использованием Counter
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Подсчет операций по категориям: {categories}")

    if not data:
        return {category: 0 for category in categories}

    # Используем Counter для подсчета всех категорий
    all_categories = [op.get('description', 'Без категории') for op in data]
    category_counter = Counter(all_categories)

    # Фильтруем только нужные категории
    result = {}
    for category in categories:
        result[category] = category_counter.get(category, 0)

    logger.info(f"Результат подсчета по категориям: {result}")
    return result


def process_bank_operations_advanced(data: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Расширенный подсчет операций по всем категориям
    """
    if not data:
        return {}

    categories = [op.get('description', 'Без категории') for op in data]
    category_counter = Counter(categories)

    return dict(category_counter.most_common())
