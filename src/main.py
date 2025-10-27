import sys
import os
from pathlib import Path
import json
import csv
import openpyxl
import re
from datetime import datetime
import logging
from collections import Counter

# Определяем корневую директорию проекта
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def setup_logging():
    """Настройка системы логирования"""
    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def transform_json_transaction(transaction):
    """Преобразование транзакции из JSON формата в единый формат"""
    if not transaction:
        return {}

    # Преобразуем дату из "2018-04-22T17:01:46.885252" в "22.04.2018"
    date_str = transaction.get('date', '')
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%d.%m.%Y')
    except (ValueError, TypeError):
        formatted_date = date_str

    # Получаем сумму и валюту
    operation_amount = transaction.get('operationAmount', {})
    amount = operation_amount.get('amount', '0')
    currency_info = operation_amount.get('currency', {})
    currency = currency_info.get('name', '')

    return {
        'id': transaction.get('id'),
        'date': formatted_date,
        'description': transaction.get('description', ''),
        'from': transaction.get('from', ''),
        'to': transaction.get('to', ''),
        'amount': amount,
        'currency': currency,
        'status': transaction.get('state', '')  # В JSON статус в поле 'state'
    }


def transform_csv_transaction(row):
    """Преобразование транзакции из CSV формата в единый формат"""
    if not row:
        return {}

    # Преобразуем дату из "2020-06-07T11:11:36Z" в "07.06.2020"
    date_str = row.get('date', '') if isinstance(row, dict) else row[2] if len(row) > 2 else ''
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%d.%m.%Y')
    except (ValueError, TypeError):
        formatted_date = date_str

    if isinstance(row, dict):
        # Если это dict (после csv.DictReader)
        return {
            'id': row.get('id', ''),
            'date': formatted_date,
            'description': row.get('description', ''),
            'from': row.get('from', ''),
            'to': row.get('to', ''),
            'amount': row.get('amount', ''),
            'currency': row.get('currency_name', '') or row.get('currency', ''),
            'status': row.get('status', '')
        }
    else:
        # Если это list (сырые данные CSV)
        return {
            'id': row[0] if len(row) > 0 else '',
            'date': formatted_date,
            'description': row[7] if len(row) > 7 else '',
            'from': row[5] if len(row) > 5 else '',
            'to': row[6] if len(row) > 6 else '',
            'amount': row[3] if len(row) > 3 else '',
            'currency': row[4] if len(row) > 4 else '',
            'status': row[1] if len(row) > 1 else ''
        }


def load_transactions_from_json(filename: str):
    """Загрузка транзакций из JSON файла"""
    filepath = DATA_DIR / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            transactions_data = json.load(f)

        # Преобразуем каждую транзакцию в единый формат
        transactions = [transform_json_transaction(tx) for tx in transactions_data]

        logging.info(f"Успешно загружено {len(transactions)} транзакций из {filepath}")

        # Отладочная информация
        if transactions:
            print(f"\nПервые 3 транзакции из JSON:")
            for i, tx in enumerate(transactions[:3], 1):
                print(f"  {i}. Статус: '{tx.get('status')}', Описание: '{tx.get('description')}'")

        return transactions
    except FileNotFoundError:
        logging.error(f"Файл {filepath} не найден")
        print(f"Файл не найден: {filepath}")
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка декодирования JSON: {e}")
        return []


def load_transactions_from_csv(filename: str):
    """Загрузка транзакций из CSV файла"""
    filepath = DATA_DIR / filename
    try:
        transactions = []

        with open(filepath, 'r', encoding='utf-8') as f:
            # Пробуем прочитать как CSV с разделителем ;
            reader = csv.reader(f, delimiter=';')

            for row in reader:
                if row:  # Пропускаем пустые строки
                    transformed_tx = transform_csv_transaction(row)
                    transactions.append(transformed_tx)

        logging.info(f"Успешно загружено {len(transactions)} транзакций из {filepath}")

        # Отладочная информация
        if transactions:
            print(f"\nПервые 3 транзакции из CSV:")
            for i, tx in enumerate(transactions[:3], 1):
                print(f"  {i}. Статус: '{tx.get('status')}', Описание: '{tx.get('description')}'")

        return transactions
    except FileNotFoundError:
        logging.error(f"Файл {filepath} не найден")
        print(f"Файл не найден: {filepath}")
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении CSV: {e}")
        return []


def load_transactions_from_xlsx(filename: str):
    """Загрузка транзакций из XLSX файла с автоматическим определением структуры"""
    filepath = DATA_DIR / filename
    try:
        transactions = []
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active

        headers = []
        for cell in sheet[1]:
            headers.append(cell.value)

        print(f"\nЗаголовки в XLSX файле: {headers}")

        # Сопоставление возможных названий полей
        field_mapping = {
            'status': ['status', 'state', 'статус', 'State', 'Status'],
            'date': ['date', 'дата', 'Date', 'Дата'],
            'description': ['description', 'описание', 'Description', 'Описание'],
            'from': ['from', 'от', 'From', 'От', 'sender'],
            'to': ['to', 'до', 'To', 'До', 'recipient'],
            'amount': ['amount', 'сумма', 'Amount', 'Сумма'],
            'currency': ['currency', 'валюта', 'Currency', 'Валюта']
        }

        # Находим соответствия
        actual_fields = {}
        for standard_field, possible_names in field_mapping.items():
            for header in headers:
                if header and header in possible_names:
                    actual_fields[standard_field] = header
                    break

        print(f"Сопоставление полей: {actual_fields}")

        # Если не нашли стандартные поля, используем позиционный подход
        if not actual_fields:
            print("Стандартные поля не найдены, используем позиционный подход")
            actual_fields = {
                'id': headers[0] if len(headers) > 0 else None,
                'status': headers[1] if len(headers) > 1 else None,
                'date': headers[2] if len(headers) > 2 else None,
                'amount': headers[3] if len(headers) > 3 else None,
                'currency': headers[4] if len(headers) > 4 else None,
                'from': headers[5] if len(headers) > 5 else None,
                'to': headers[6] if len(headers) > 6 else None,
                'description': headers[7] if len(headers) > 7 else None,
            }

        for i, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), 2):
            transaction = {}

            # Заполняем стандартные поля
            for standard_field, actual_field in actual_fields.items():
                if actual_field and actual_field in headers:
                    value_index = headers.index(actual_field)
                    transaction[standard_field] = row[value_index] if value_index < len(row) else None
                else:
                    transaction[standard_field] = None

            # Преобразуем дату если нужно
            if transaction.get('date') and isinstance(transaction['date'], str):
                try:
                    date_obj = datetime.fromisoformat(transaction['date'].replace('Z', '+00:00'))
                    transaction['date'] = date_obj.strftime('%d.%m.%Y')
                except (ValueError, TypeError):
                    pass

            # Выводим первую транзакцию для отладки
            if i == 2:
                print(f"Первая транзакция (преобразованная):")
                for key, value in transaction.items():
                    print(f"  {key}: '{value}'")

            transactions.append(transaction)

        logging.info(f"Успешно загружено {len(transactions)} транзакций из {filepath}")

        # Отладочная информация
        if transactions:
            print(f"\nПервые 3 транзакции из XLSX:")
            for i, tx in enumerate(transactions[:3], 1):
                print(f"  {i}. Статус: '{tx.get('status')}', Описание: '{tx.get('description')}'")

        return transactions
    except FileNotFoundError:
        logging.error(f"Файл {filepath} не найден")
        print(f"Файл не найден: {filepath}")
        return []
    except Exception as e:
        logging.error(f"Ошибка при чтении XLSX: {e}")
        return []


# Функции обработки транзакций
def filter_by_status(transactions, status: str):
    """Фильтрация транзакций по статусу"""
    if not transactions or transactions is None:
        return []

    if not status:
        return transactions  # Возвращаем все если статус не указан

    status_lower = status.lower()
    filtered = [
        t for t in transactions
        if t.get('status') and str(t.get('status', '')).lower() == status_lower
    ]

    logging.info(f"Отфильтровано по статусу '{status}': {len(filtered)} транзакций")
    return filtered


def sort_by_date(transactions, reverse: bool = False):
    """Сортировка транзакций по дате"""
    if not transactions or transactions is None:
        return []

    def get_date(transaction):
        date_str = str(transaction.get('date', ''))
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except (ValueError, TypeError):
            try:
                return datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                return datetime.min  # Для некорректных дат возвращаем минимальную дату

    return sorted(transactions, key=get_date, reverse=reverse)


def filter_rub_transactions(transactions):
    """Фильтрация рублевых транзакций"""
    if not transactions or transactions is None:
        return []

    rub_transactions = [
        t for t in transactions
        if
        t.get('currency') and str(t.get('currency', '')).lower() in ['rub', 'руб', 'рубль', 'rur', 'RUB', 'RUR', 'руб.']
    ]

    logging.info(f"Отфильтровано рублевых транзакций: {len(rub_transactions)}")
    return rub_transactions


def search_in_description(transactions, search_word: str):
    """Поиск транзакций по слову в описании"""
    if not transactions or transactions is None:
        return []  # Всегда возвращаем пустой список для None или пустых данных

    if not search_word:
        return transactions  # Возвращаем все транзакции если поиск пустой

    try:
        pattern = re.compile(re.escape(search_word), re.IGNORECASE)
        filtered = [
            t for t in transactions
            if t.get('description') and pattern.search(str(t.get('description', '')))
        ]

        logging.info(f"Найдено транзакций по слову '{search_word}': {len(filtered)}")
        return filtered

    except re.error as e:
        logging.error(f"Ошибка в регулярном выражении '{search_word}': {e}")
        return []


def count_operations_by_category(transactions: list) -> dict:
    """
    Подсчет операций по категориям с использованием Counter

    Args:
        transactions: список транзакций

    Returns:
        Словарь с количеством операций по категориям
    """
    if not transactions or transactions is None:
        return {}

    # Извлекаем категории (описания) из транзакций
    categories = [tx.get('description', 'Без категории') for tx in transactions]

    # Используем Counter для подсчета
    category_counter = Counter(categories)

    # Сортируем по убыванию количества операций
    sorted_categories = dict(category_counter.most_common())

    logging.info(f"Подсчитано операций по категориям: {len(sorted_categories)} категорий")
    return sorted_categories


def count_operations_by_status_counter(transactions: list) -> dict:
    """
    Подсчет операций по статусам с использованием Counter

    Args:
        transactions: список транзакций

    Returns:
        Словарь с количеством операций по статусам
    """
    if not transactions or transactions is None:
        return {}

    statuses = [tx.get('status', 'Без статуса') for tx in transactions]
    status_counter = Counter(statuses)

    return dict(status_counter.most_common())


def print_statistics(transactions: list):
    """Вывод статистики по операциям"""
    if not transactions:
        print("Нет данных для статистики")
        return

    category_stats = count_operations_by_category(transactions)
    status_stats = count_operations_by_status_counter(transactions)

    print("\n" + "=" * 60)
    print("СТАТИСТИКА ОПЕРАЦИЙ")
    print("=" * 60)

    print("\n📊 По категориям:")
    for category, count in category_stats.items():
        print(f"  {category}: {count} операций")

    print(f"\n📈 По статусам:")
    for status, count in status_stats.items():
        print(f"  {status}: {count} операций")

    print(f"\n📋 Всего операций: {len(transactions)}")
    print("=" * 60)


def mask_card_number(card_number: str) -> str:
    """Маскировка номера карты"""
    if not card_number:
        return ""

    card_str = str(card_number).replace(' ', '')
    if len(card_str) < 16:
        return str(card_number)

    return f"{card_str[:4]} {card_str[4:6]}** **** {card_str[-4:]}"


def mask_account_number(account_number: str) -> str:
    """Маскировка номера счета"""
    if not account_number:
        return ""

    account_str = str(account_number).replace(' ', '')
    if len(account_str) < 4:
        return str(account_number)

    return f"Счет **{account_str[-4:]}"


# Функции взаимодействия с пользователем
def get_user_choice(options: list, prompt: str) -> str:
    """Получение выбора пользователя с валидацией"""
    while True:
        try:
            print(prompt)
            for i, option in enumerate(options, 1):
                print(f"{i}. {option}")

            choice = input("Ваш выбор: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1]
            else:
                print("Пожалуйста, введите номер из предложенных вариантов")
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            exit()
        except Exception as e:
            print(f"Произошла ошибка: {e}")


def get_status_filter(available_statuses: list) -> str:
    """Получение статуса для фильтрации"""
    while True:
        try:
            print(f"\nВведите статус, по которому необходимо выполнить фильтрацию.")
            print(f"Доступные для фильтрации статусы: {', '.join(available_statuses)}")

            status = input("Статус: ").strip().upper()

            if status in available_statuses:
                return status
            else:
                print(f'Статус операции "{status}" недоступен.')
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            exit()


def get_yes_no_input(prompt: str) -> bool:
    """Получение ответа Да/Нет от пользователя"""
    while True:
        try:
            response = input(f"{prompt} (Да/Нет): ").strip().lower()
            if response in ['да', 'д', 'yes', 'y']:
                return True
            elif response in ['нет', 'н', 'no', 'n']:
                return False
            else:
                print("Пожалуйста, введите 'Да' или 'Нет'")
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            exit()


def get_sort_direction() -> bool:
    """Получение направления сортировки"""
    while True:
        try:
            direction = input("Отсортировать по возрастанию или по убыванию? ").strip().lower()
            if direction in ['по возрастанию', 'возрастание', 'возрастанию', 'asc']:
                return False
            elif direction in ['по убыванию', 'убывание', 'убыванию', 'desc']:
                return True
            else:
                print("Пожалуйста, введите 'по возрастанию' или 'по убыванию'")
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            exit()


def get_search_word() -> str:
    """Получение слова для поиска в описании"""
    while True:
        try:
            search_word = input("Введите слово для поиска в описании: ").strip()
            if search_word:
                return search_word
            else:
                print("Пожалуйста, введите непустое слово для поиска")
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            exit()


def get_available_statuses(transactions: list) -> list:
    """Получение списка доступных статусов"""
    if not transactions or transactions is None:
        return []

    statuses = set()
    empty_status_count = 0

    for i, transaction in enumerate(transactions):
        status = transaction.get('status')
        if status:
            statuses.add(str(status).upper())
        else:
            empty_status_count += 1

    print(f"\nНайдены статусы: {list(statuses)}")
    if empty_status_count > 0:
        print(f"Транзакций без статуса: {empty_status_count}")

    return sorted(list(statuses))


def format_transaction(transaction: dict) -> str:
    """Форматирование транзакции для вывода"""
    date = transaction.get('date', 'Дата не указана')
    description = transaction.get('description', 'Описание отсутствует')
    amount = transaction.get('amount', 0)
    currency = transaction.get('currency', 'руб.')

    from_account = transaction.get('from', '')
    to_account = transaction.get('to', '')

    # Маскируем номера
    if from_account:
        from_str = str(from_account)
        if from_str.lower().startswith('счет'):
            from_display = mask_account_number(from_str)
        else:
            from_display = mask_card_number(from_str)
    else:
        from_display = "Не указан"

    if to_account:
        to_str = str(to_account)
        if to_str.lower().startswith('счет'):
            to_display = mask_account_number(to_str)
        else:
            to_display = mask_card_number(to_str)
    else:
        to_display = "Не указан"

    result = f"{date} {description}\n"

    if from_account and to_account:
        result += f"{from_display} -> {to_display}\n"
    elif from_account:
        result += f"{from_display}\n"
    elif to_account:
        result += f"{to_display}\n"

    result += f"Сумма: {amount} {currency}\n"

    return result


def print_transactions(transactions: list):
    """Вывод списка транзакций"""
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"\nВсего банковских операций в выборке: {len(transactions)}\n")
    print("=" * 50)

    for i, transaction in enumerate(transactions, 1):
        print(f"{i}. {format_transaction(transaction)}")
        print("-" * 50)


def list_available_files():
    """Показать доступные файлы в папке data"""
    print(f"\nПроверяем папку: {DATA_DIR}")
    if DATA_DIR.exists():
        print("Доступные файлы в data:")
        files = list(DATA_DIR.glob("*"))
        if files:
            for file in files:
                print(f"  - {file.name}")
        else:
            print("  (папка пуста)")
    else:
        print(f"Папка {DATA_DIR} не найдена")


def main():
    """Основная функция приложения"""
    setup_logging()
    logger = logging.getLogger(__name__)

    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    try:
        # Показываем доступные файлы
        list_available_files()

        # Выбор типа файла
        file_types = [
            "Получить информацию о транзакциях из JSON-файла",
            "Получить информацию о транзакциях из CSV-файла",
            "Получить информацию о транзакциях из XLSX-файла"
        ]

        file_choice = get_user_choice(file_types, "\nВыберите необходимый пункт меню:")

        # Загрузка данных с правильными именами файлов
        if "JSON" in file_choice:
            filename = "operations"  # Ваш файл operations (без .json)
            transactions = load_transactions_from_json(filename)
            print("Для обработки выбран JSON-файл.")
        elif "CSV" in file_choice:
            filename = "transactions.csv"  # Ваш файл transactions.csv
            transactions = load_transactions_from_csv(filename)
            print("Для обработки выбран CSV-файл.")
        else:
            filename = "transactions_excel.xlsx"  # Ваш xlsx файл
            transactions = load_transactions_from_xlsx(filename)
            print("Для обработки выбран XLSX-файл.")

        if not transactions:
            print("Не удалось загрузить транзакции или файл пуст.")
            list_available_files()
            return

        # Показываем общую статистику
        print_statistics(transactions)

        # Фильтрация по статусу
        available_statuses = get_available_statuses(transactions)
        if not available_statuses:
            print("В файле не найдено транзакций с указанными статусами.")
            return

        status = get_status_filter(available_statuses)
        filtered_transactions = filter_by_status(transactions, status)
        print(f"Операции отфильтрованы по статусу '{status}'")

        if not filtered_transactions:
            print("Не найдено транзакций с выбранным статусом.")
            return

        # Дополнительные фильтры
        current_transactions = filtered_transactions

        # Сортировка по дате
        if get_yes_no_input("\nОтсортировать операции по дате?"):
            sort_reverse = get_sort_direction()
            current_transactions = sort_by_date(current_transactions, sort_reverse)
            direction = "по убыванию" if sort_reverse else "по возрастанию"
            print(f"Операции отсортированы {direction}")

        # Фильтрация рублевых транзакций
        if get_yes_no_input("\nВыводить только рублевые транзакции?"):
            current_transactions = filter_rub_transactions(current_transactions)
            print("Выводятся только рублевые транзакции")

        # Поиск по описанию
        if get_yes_no_input("\nОтфильтровать список транзакций по определенному слову в описании?"):
            search_word = get_search_word()
            current_transactions = search_in_description(current_transactions, search_word)
            print(f"Применен фильтр по слову '{search_word}'")

        # Показываем статистику по отфильтрованным данным
        if current_transactions != filtered_transactions:
            print(f"\nСтатистика по отфильтрованным данным:")
            print_statistics(current_transactions)

        # Вывод результатов
        print("\nРаспечатываю итоговый список транзакций...")
        print_transactions(current_transactions)

        logger.info("Программа успешно завершена")

    except Exception as e:
        logger.error(f"Ошибка в работе программы: {e}")
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
