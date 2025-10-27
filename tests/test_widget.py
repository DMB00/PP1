"""
Виджеты для пользовательского интерфейса
"""

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class TransactionWidget:
    """Виджет для отображения транзакций"""

    def __init__(self, max_display: int = 10):
        self.max_display = max_display
        self.transactions = []

    def add_transaction(self, transaction: dict) -> None:
        """Добавить транзакцию в виджет"""
        try:
            if transaction and isinstance(transaction, dict):
                self.transactions.append(transaction)
                logger.debug(f"Добавлена транзакция: {transaction.get('id', 'unknown')}")
            else:
                logger.warning("Попытка добавить некорректную транзакцию")
        except Exception as e:
            logger.error(f"Ошибка при добавлении транзакции: {e}")

    def display(self) -> str:
        """Отобразить транзакции в виде строки"""
        if not self.transactions:
            return "Нет транзакций для отображения"

        result = []
        for i, transaction in enumerate(self.transactions[:self.max_display], 1):
            date = transaction.get('date', 'Неизвестно')
            description = transaction.get('description', 'Без описания')
            amount = transaction.get('amount', 0)
            currency = transaction.get('currency', 'RUB')

            result.append(f"{i}. {date} {description} - {amount} {currency}")

        return "\n".join(result)

    def clear(self) -> None:
        """Очистить список транзакций"""
        self.transactions.clear()
        logger.info("Список транзакций очищен")

    def get_transaction_count(self) -> int:
        """Получить количество транзакций"""
        return len(self.transactions)

    def filter_by_currency(self, currency: str) -> List[dict]:
        """Фильтровать транзакции по валюте"""
        if not currency:
            return self.transactions

        filtered = [
            tx for tx in self.transactions
            if tx.get('currency', '').lower() == currency.lower()
        ]
        logger.info(f"Отфильтровано {len(filtered)} транзакций по валюте {currency}")
        return filtered


class SearchWidget:
    """Виджет для поиска транзакций"""

    def __init__(self):
        self.search_history = []

    def search_in_description(self, transactions: List[dict], keyword: str) -> List[dict]:
        """Поиск транзакций по ключевому слову в описании"""
        if not transactions or not keyword:
            return []

        keyword_lower = keyword.lower()
        results = [
            tx for tx in transactions
            if keyword_lower in tx.get('description', '').lower()
        ]

        # Сохраняем в историю поиска
        self.search_history.append({
            'keyword': keyword,
            'results_count': len(results),
            'timestamp': 'now'  # В реальном приложении здесь был бы datetime
        })

        logger.info(f"Найдено {len(results)} транзакций по ключевому слову '{keyword}'")
        return results

    def get_search_history(self) -> List[dict]:
        """Получить историю поиска"""
        return self.search_history.copy()

    def clear_history(self) -> None:
        """Очистить историю поиска"""
        self.search_history.clear()
        logger.info("История поиска очищена")


def create_transaction_widget() -> TransactionWidget:
    """Создать виджет транзакций"""
    return TransactionWidget()


def create_search_widget() -> SearchWidget:
    """Создать виджет поиска"""
    return SearchWidget()
