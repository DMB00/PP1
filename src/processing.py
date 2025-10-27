"""
Модуль для обработки банковских операций.
Содержит функции для фильтрации и анализа финансовых данных.
"""

import re
from collections import Counter
from typing import List, Dict, Any


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """
    Фильтрует банковские операции по строке поиска в описании.

    Args:
        data: Список словарей с данными о банковских операциях
        search: Строка для поиска в описании операций

    Returns:
        List[Dict[str, Any]]: Отфильтрованный список операций,
                             где в описании найдена строка поиска

    Example:
        >>> operations = [{'description': 'Перевод организации'}, {'description': 'Оплата услуг'}]
        >>> process_bank_search(operations, 'Перевод')
        [{'description': 'Перевод организации'}]
    """
    if not data or not search:
        return []

    try:
        # Создаем регулярное выражение для поиска (регистронезависимое)
        pattern = re.compile(re.escape(search), re.IGNORECASE)

        # Фильтруем операции, где описание соответствует поисковому запросу
        filtered_operations = [
            operation for operation in data
            if operation.get('description') and pattern.search(str(operation['description']))
        ]

        return filtered_operations

    except re.error as e:
        # В случае ошибки в регулярном выражении возвращаем пустой список
        print(f"Ошибка в регулярном выражении '{search}': {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка при поиске: {e}")
        return []


def count_operations_by_category(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество операций по заданным категориям.

    Args:
        data: Список словарей с данными о банковских операциях
        categories: Список категорий для подсчета

    Returns:
        Dict[str, int]: Словарь, где ключи - названия категорий,
                       значения - количество операций в каждой категории

    Example:
        >>> operations = [{'description': 'Перевод'}, {'description': 'Оплата'}, {'description': 'Перевод'}]
        >>> count_operations_by_category(operations, ['Перевод', 'Оплата', 'Вывод'])
        {'Перевод': 2, 'Оплата': 1, 'Вывод': 0}
    """
    if not data:
        return {category: 0 for category in categories}

    # Извлекаем все описания из операций
    descriptions = [str(operation.get('description', '')).strip() for operation in data]

    # Используем Counter для подсчета всех операций
    all_counts = Counter(descriptions)

    # Создаем результат только для запрошенных категорий
    result = {}
    for category in categories:
        # Приводим категорию к строке и убираем пробелы для сравнения
        category_str = str(category).strip()
        result[category] = all_counts.get(category_str, 0)

    return result


# Дополнительная утилитарная функция для получения всех уникальных категорий
def get_all_categories(data: List[Dict[str, Any]]) -> List[str]:
    """
    Возвращает список всех уникальных категорий из данных об операциях.

    Args:
        data: Список словарей с данными о банковских операциях

    Returns:
        List[str]: Список уникальных категорий
    """
    if not data:
        return []

    categories = set()
    for operation in data:
        description = operation.get('description')
        if description:
            categories.add(str(description).strip())

    return sorted(list(categories))
