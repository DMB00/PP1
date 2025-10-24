import os
import sys
from typing import List, Dict, Any
from datetime import datetime

# Абсолютные импорты
from financial_reader import FinancialDataReader
from masks import get_mask_card_number, get_mask_account


class BankTransactionManager:
    """Основной класс для управления банковскими транзакциями"""

    def __init__(self):
        self.reader = FinancialDataReader()
        self.transactions = []
        self.filtered_transactions = []

        # Доступные статусы операций
        self.available_statuses = ['EXECUTED', 'CANCELED', 'PENDING']

    def clear_screen(self):
        """Очистка экрана консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Вывод заголовка программы"""
        print("=" * 60)
        print("       ПРОГРАММА РАБОТЫ С БАНКОВСКИМИ ТРАНЗАКЦИЯМИ")
        print("=" * 60)
        print()

    def get_user_choice(self, prompt: str, valid_choices: List[str]) -> str:
        """
        Получение выбора пользователя с валидацией
        """
        while True:
            choice = input(prompt).strip()
            if choice in valid_choices:
                return choice
            print(f"Неверный выбор. Допустимые варианты: {', '.join(valid_choices)}")
            print()

    def get_yes_no_choice(self, prompt: str) -> bool:
        """
        Получение ответа Да/Нет от пользователя
        """
        while True:
            choice = input(prompt).strip().lower()
            if choice in ['да', 'д', 'yes', 'y']:
                return True
            elif choice in ['нет', 'н', 'no', 'n']:
                return False
            print("Пожалуйста, введите 'Да' или 'Нет'")
            print()

    def process_bank_search(self, data: List[Dict], search: str) -> List[Dict]:
        """
        Упрощенная версия поиска по описанию
        """
        if not data or not search:
            return []

        filtered_data = []
        search_lower = search.lower()

        for operation in data:
            if operation.get('description'):
                description = str(operation['description']).lower()
                if search_lower in description:
                    filtered_data.append(operation)

        return filtered_data

    def load_transactions_from_file(self, file_type: str) -> bool:
        """
        Загрузка транзакций из файла
        """
        try:
            # Для демонстрации используем тестовые данные
            if file_type == 'json':
                print("Обработка JSON файлов временно недоступна")
                return False
            elif file_type in ['csv', 'xlsx']:
                # Создаем тестовые данные для демонстрации
                self.transactions = [
                    {
                        'id': 1,
                        'state': 'EXECUTED',
                        'date': '2023-09-05T11:30:32',
                        'amount': 1500.00,
                        'currency_name': 'Ruble',
                        'currency_code': 'RUB',
                        'from_account': 'Счет 58803664561298323391',
                        'to_account': 'Счет 39745660563456619397',
                        'description': 'Перевод организации'
                    },
                    {
                        'id': 2,
                        'state': 'EXECUTED',
                        'date': '2023-09-06T12:00:00',
                        'amount': 2500.00,
                        'currency_name': 'Ruble',
                        'currency_code': 'RUB',
                        'from_account': 'Visa 1234567812345678',
                        'to_account': 'MasterCard 8765432187654321',
                        'description': 'Перевод с карты на карту'
                    },
                    {
                        'id': 3,
                        'state': 'CANCELED',
                        'date': '2023-09-07T13:00:00',
                        'amount': 3000.00,
                        'currency_name': 'Ruble',
                        'currency_code': 'RUB',
                        'from_account': '',
                        'to_account': 'Счет 12345678901234567890',
                        'description': 'Открытие вклада'
                    },
                    {
                        'id': 4,
                        'state': 'EXECUTED',
                        'date': '2023-09-08T14:00:00',
                        'amount': 4000.00,
                        'currency_name': 'Ruble',
                        'currency_code': 'RUB',
                        'from_account': 'Счет 11112222333344445555',
                        'to_account': 'Счет 66667777888899990000',
                        'description': 'Оплата услуг'
                    },
                    {
                        'id': 5,
                        'state': 'EXECUTED',
                        'date': '2023-09-09T15:00:00',
                        'amount': 500.00,
                        'currency_name': 'Dollar',
                        'currency_code': 'USD',
                        'from_account': 'Visa 1111222233334444',
                        'to_account': 'MasterCard 5555666677778888',
                        'description': 'Международный перевод'
                    }
                ]
                print(f"Успешно загружено {len(self.transactions)} тестовых транзакций")
                return True
            else:
                print(f"Неподдерживаемый тип файла: {file_type}")
                return False

        except Exception as e:
            print(f"Ошибка при загрузке файла: {e}")
            return False

    def filter_by_status(self):
        """Фильтрация транзакций по статусу"""
        print("\n" + "=" * 50)
        print("ФИЛЬТРАЦИЯ ПО СТАТУСУ")
        print("=" * 50)

        while True:
            print(f"Доступные для фильтрации статусы: {', '.join(self.available_statuses)}")
            status = input("Введите статус, по которому необходимо выполнить фильтрацию: ").strip().upper()

            if status in self.available_statuses:
                self.filtered_transactions = [
                    t for t in self.transactions
                    if t.get('state', '').upper() == status
                ]
                print(f"Операции отфильтрованы по статусу '{status}'")
                print(f"Найдено операций: {len(self.filtered_transactions)}")
                break
            else:
                print(f"Статус операции '{status}' недоступен.")
                print()

    def sort_transactions(self):
        """Сортировка транзакций по дате"""
        if not self.get_yes_no_choice("Отсортировать операции по дате? (Да/Нет): "):
            return

        order_choice = self.get_user_choice(
            "Отсортировать по возрастанию или по убыванию? (возрастание/убывание): ",
            ['возрастание', 'убывание']
        )

        try:
            # Сортировка по дате
            self.filtered_transactions.sort(
                key=lambda x: datetime.fromisoformat(x['date'].replace('Z', '')),
                reverse=(order_choice == 'убывание')
            )
            print(f"Операции отсортированы по дате ({order_choice})")
        except Exception as e:
            print(f"Ошибка при сортировке: {e}")

    def filter_by_currency(self):
        """Фильтрация транзакций по валюте"""
        if not self.get_yes_no_choice("Выводить только рублевые транзакции? (Да/Нет): "):
            return

        original_count = len(self.filtered_transactions)
        self.filtered_transactions = [
            t for t in self.filtered_transactions
            if t.get('currency_code', '').upper() == 'RUB'
        ]
        filtered_count = len(self.filtered_transactions)
        print(f"Отфильтрованы только рублевые транзакции (осталось {filtered_count} из {original_count})")

    def filter_by_description(self):
        """Фильтрация транзакций по ключевому слову в описании"""
        if not self.get_yes_no_choice("Отфильтровать список транзакций по определенному слову в описании? (Да/Нет): "):
            return

        keyword = input("Введите слово для поиска в описании: ").strip()
        if keyword:
            original_count = len(self.filtered_transactions)
            self.filtered_transactions = self.process_bank_search(self.filtered_transactions, keyword)
            filtered_count = len(self.filtered_transactions)
            print(
                f"Отфильтрованы транзакции по ключевому слову '{keyword}' (осталось {filtered_count} из {original_count})")

    def format_amount(self, transaction: Dict[str, Any]) -> str:
        """Форматирование суммы транзакции"""
        amount = transaction.get('amount', 0)
        currency_code = transaction.get('currency_code', '')
        currency_name = transaction.get('currency_name', '')

        if currency_code == 'RUB':
            return f"{amount:,.2f} руб.".replace(',', ' ')
        else:
            return f"{amount:,.2f} {currency_name} ({currency_code})".replace(',', ' ')

    def format_account_info(self, account_str: str) -> str:
        """Форматирование информации о счете/карте"""
        if not account_str:
            return "Не указано"

        # Определяем тип счета/карты
        account_lower = account_str.lower()

        if 'счет' in account_lower or 'account' in account_lower:
            # Это счет - маскируем как счет
            return get_mask_account(account_str)
        elif any(card in account_lower for card in ['visa', 'mastercard', 'maestro', 'american express']):
            # Это карта - маскируем как карту
            return get_mask_card_number(account_str)
        else:
            # Неизвестный тип - возвращаем как есть
            return account_str

    def format_date(self, date_str: str) -> str:
        """Форматирование даты"""
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', ''))
            return date_obj.strftime("%d.%m.%Y")
        except:
            return date_str

    def print_transaction(self, transaction: Dict[str, Any], index: int):
        """Вывод информации о транзакции"""
        print(f"\n--- Транзакция {index + 1} ---")
        print(f"Дата: {self.format_date(transaction['date'])}")
        print(f"Описание: {transaction['description']}")
        print(f"Статус: {transaction['state']}")
        print(f"Сумма: {self.format_amount(transaction)}")

        # Информация об отправителе и получателе
        from_account = transaction.get('from_account', '')
        to_account = transaction.get('to_account', '')

        if from_account and to_account:
            print(f"От: {self.format_account_info(from_account)}")
            print(f"Кому: {self.format_account_info(to_account)}")
        elif to_account:
            print(f"Получатель: {self.format_account_info(to_account)}")

        print("-" * 40)

    def print_transactions(self):
        """Вывод всех отфильтрованных транзакций"""
        if not self.filtered_transactions:
            print("\nНе найдено ни одной транзакции, подходящей под ваши условия фильтрации")
            return

        print(f"\n{'=' * 60}")
        print(f"РАСПЕЧАТЫВАЮ ИТОГОВЫЙ СПИСОК ТРАНЗАКЦИЙ...")
        print(f"{'=' * 60}")
        print(f"Всего банковских операций в выборке: {len(self.filtered_transactions)}\n")

        for i, transaction in enumerate(self.filtered_transactions):
            self.print_transaction(transaction, i)

    def run(self):
        """Основной цикл программы"""
        self.clear_screen()
        self.print_header()

        print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
        print("Выберите необходимый пункт меню:")
        print("1. Получить информацию о транзакциях из JSON-файла")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла")
        print()

        # Выбор типа файла
        file_choice = self.get_user_choice("Ваш выбор (1-3): ", ['1', '2', '3'])

        file_types = {
            '1': ('json', 'JSON-файл'),
            '2': ('csv', 'CSV-файл'),
            '3': ('xlsx', 'XLSX-файл')
        }

        file_type, file_name = file_types[file_choice]
        print(f"Для обработки выбран {file_name}.")

        # Загрузка транзакций
        if not self.load_transactions_from_file(file_type):
            print("Не удалось загрузить транзакции. Программа завершена.")
            return

        # Если транзакции загружены, продолжаем
        if self.transactions:
            # Фильтрация по статусу
            self.filter_by_status()

            # Применяем дополнительные фильтры только если есть отфильтрованные транзакции
            if self.filtered_transactions:
                # Сортировка
                self.sort_transactions()

                # Фильтрация по валюте
                self.filter_by_currency()

                # Фильтрация по описанию
                self.filter_by_description()

            # Вывод результатов
            self.print_transactions()

        print("\n" + "=" * 60)
        print("Спасибо за использование программы! До свидания!")
        print("=" * 60)


def main():
    """Основная функция программы"""
    try:
        manager = BankTransactionManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\nПрограмма прервана пользователем.")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")
        print("Программа завершена.")


if __name__ == "__main__":
    main()
