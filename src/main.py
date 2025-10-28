# main.py
import json
import csv
import openpyxl
from datetime import datetime
import logging
from collections import Counter
from pathlib import Path

# Определяем корневую директорию проекта
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# Настройка логирования
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


# Функции маскировки
def mask_card_number(card_number: str) -> str:
    """Маскировка номера карты с сохранением названия"""
    if not card_number:
        return ""

    card_str = str(card_number)

    # Ищем цифры в строке
    digits = ''.join(filter(str.isdigit, card_str))

    if len(digits) < 16:
        return card_str

    # Маскируем цифровую часть
    masked_digits = f"{digits[:4]} {digits[4:6]}** **** {digits[-4:]}"

    # Сохраняем текстовую часть
    text_part = ''.join(c for c in card_str if not c.isdigit()).strip()

    if text_part:
        return f"{text_part} {masked_digits}"
    else:
        return masked_digits


def mask_account_number(account_number: str) -> str:
    """Маскировка номера счета с сохранением названия"""
    if not account_number:
        return ""

    account_str = str(account_number)

    # Ищем цифры в строке
    digits = ''.join(filter(str.isdigit, account_str))

    if len(digits) < 4:
        return account_str

    # Маскируем цифровую часть
    masked_digits = f"**{digits[-4:]}"

    # Сохраняем текстовую часть
    text_part = ''.join(c for c in account_str if not c.isdigit()).strip()

    if text_part:
        return f"{text_part} {masked_digits}"
    else:
        return f"Счет {masked_digits}"


# Функции преобразования данных
def transform_json_transaction(transaction):
    """Преобразование транзакции из JSON формата в единый формат"""
    if not transaction:
        return {}

    # Преобразуем дату
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
        'status': transaction.get('state', '')
    }


def transform_csv_transaction(row):
    """Преобразование транзакции из CSV формата в единый формат"""
    if not row:
        return {}

    date_str = row.get('date', '') if isinstance(row, dict) else row[2] if len(row) > 2 else ''
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%d.%m.%Y')
    except (ValueError, TypeError):
        formatted_date = date_str

    if isinstance(row, dict):
        return {
            'id': row.get('id', ''),
            'date': formatted_date,
            'description': row.get('description', ''),
            'from': row.get('from', ''),
            'to': row.get('to', ''),
            'amount': row.get('amount', ''),
            'currency': row.get('currency_name', '') or row.get('currency', ''),
            'status': row.get('state', '') or row.get('status', '')
        }
    else:
        return {
            'id': row[0] if len(row) > 0 else '',
            'date': formatted_date,
            'description': row[7] if len(row) > 7 else '',
            'from': row[5] if len(row) > 5 else '',
            'to': row[6] if len(row) > 6 else '',
            'amount': str(row[3]) if len(row) > 3 else '',
            'currency': str(row[4]) if len(row) > 4 else '',
            'status': row[1] if len(row) > 1 else ''
        }


# Функции загрузки данных
def load_transactions_from_json():
    """Загрузка транзакций из JSON файла"""
    try:
        # Ищем JSON файлы
        json_files = list(DATA_DIR.glob("*.json"))
        if not json_files:
            operations_file = DATA_DIR / "operations"
            if operations_file.exists():
                json_files = [operations_file]
            else:
                print("JSON файлы не найдены в папке data")
                return []

        filepath = json_files[0]
        with open(filepath, 'r', encoding='utf-8') as f:
            transactions_data = json.load(f)

        # Обрабатываем разные форматы данных
        if isinstance(transactions_data, dict):
            transactions_data = [transactions_data]
        elif not isinstance(transactions_data, list):
            transactions_data = []

        transactions = [transform_json_transaction(tx) for tx in transactions_data if tx]
        logging.info(f"Успешно загружено {len(transactions)} транзакций из {filepath}")
        return transactions

    except Exception as e:
        logging.error(f"Ошибка при загрузке JSON: {e}")
        return []


def load_transactions_from_csv():
    """Загрузка транзакций из CSV файла"""
    try:
        csv_files = list(DATA_DIR.glob("*.csv"))
        if not csv_files:
            print("CSV файлы не найдены в папке data")
            return []

        filepath = csv_files[0]
        transactions = []

        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                if row:
                    transformed_tx = transform_csv_transaction(row)
                    transactions.append(transformed_tx)

        logging.info(f"Успешно загружено {len(transactions)} транзакций из {filepath}")
        return transactions
    except Exception as e:
        logging.error(f"Ошибка при чтении CSV: {e}")
        return []


def load_transactions_from_xlsx():
    """Загрузка транзакций из XLSX файла"""
    try:
        xlsx_files = list(DATA_DIR.glob("*.xlsx"))
        if not xlsx_files:
            print("XLSX файлы не найдены в папке data")
            return []

        filepath = xlsx_files[0]
        transactions = []
        workbook = openpyxl.load_workbook(filepath)
        sheet = workbook.active

        headers = [cell.value for cell in sheet[1] if cell.value]

        # Сопоставление полей
        field_mapping = {
            'status': ['state', 'status', 'State', 'Status'],
            'date': ['date', 'Date'],
            'description': ['description', 'Description'],
            'from': ['from', 'From'],
            'to': ['to', 'To'],
            'amount': ['amount', 'Amount'],
            'currency': ['currency_name', 'currency', 'Currency']
        }

        # Находим соответствия
        column_mapping = {}
        for standard_field, possible_names in field_mapping.items():
            for header in headers:
                if header in possible_names:
                    column_mapping[standard_field] = headers.index(header)
                    break

        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not any(row):
                continue

            transaction = {}
            for field, col_index in column_mapping.items():
                if col_index < len(row):
                    transaction[field] = row[col_index]

            # Преобразуем дату если нужно
            if transaction.get('date') and isinstance(transaction['date'], str):
                try:
                    date_obj = datetime.fromisoformat(transaction['date'].replace('Z', '+00:00'))
                    transaction['date'] = date_obj.strftime('%d.%m.%Y')
                except (ValueError, TypeError):
                    pass

            transactions.append(transaction)

        logging.info(f"Успешно загружено {len(transactions)} транзакций из {filepath}")
        return transactions
    except Exception as e:
        logging.error(f"Ошибка при чтении XLSX: {e}")
        return []


# Функции фильтрации и сортировки
def filter_by_status(transactions, status: str):
    """Фильтрация транзакций по статусу"""
    if not transactions:
        return []

    status_lower = status.lower()
    filtered = [
        t for t in transactions
        if t.get('status') and str(t.get('status', '')).lower() == status_lower
    ]
    return filtered


def sort_by_date(transactions, reverse: bool = False):
    """Сортировка транзакций по дате"""
    if not transactions:
        return []

    def get_date(transaction):
        date_str = str(transaction.get('date', ''))
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except ValueError:
            return datetime.min

    return sorted(transactions, key=get_date, reverse=reverse)


def filter_rub_transactions(transactions):
    """Фильтрация рублевых транзакций"""
    if not transactions:
        return []

    rub_transactions = [
        t for t in transactions
        if t.get('currency') and any(rub_word in str(t.get('currency', '')).lower()
                                     for rub_word in ['руб', 'rub', 'rur'])
    ]
    return rub_transactions


def filter_by_description(transactions: list, search_word: str):
    """Фильтрация транзакций по ключевому слову в описании"""
    if not transactions or not search_word:
        return transactions

    search_word_lower = search_word.lower()
    filtered = [
        t for t in transactions
        if t.get('description') and search_word_lower in str(t.get('description', '')).lower()
    ]
    return filtered


# Функции взаимодействия с пользователем
def get_user_choice(options: list, prompt: str) -> str:
    """Получение выбора пользователя"""
    while True:
        try:
            print(f"\n{prompt}")
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
    """Получение ответа Да/Нет"""
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
    """Получение ключевого слова для поиска"""
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
    if not transactions:
        return []

    statuses = set()
    for transaction in transactions:
        status = transaction.get('status')
        if status:
            statuses.add(str(status).upper())

    return sorted(list(statuses))


# Функции форматирования и вывода
def format_transaction(transaction: dict) -> str:
    """Форматирование транзакции для вывода"""
    date = transaction.get('date', '')
    description = transaction.get('description', '')
    amount = transaction.get('amount', '0')
    currency = transaction.get('currency', '')

    from_account = transaction.get('from', '')
    to_account = transaction.get('to', '')

    # Маскируем номера
    from_display = ""
    to_display = ""

    if from_account:
        from_str = str(from_account)
        if 'счет' in from_str.lower():
            from_display = mask_account_number(from_str)
        else:
            from_display = mask_card_number(from_str)

    if to_account:
        to_str = str(to_account)
        if 'счет' in to_str.lower():
            to_display = mask_account_number(to_str)
        else:
            to_display = mask_card_number(to_str)

    # Форматируем вывод
    result = f"{date} {description}\n"

    if from_account and to_account:
        result += f"{from_display} -> {to_display}\n"
    elif from_account:
        result += f"{from_display}\n"
    elif to_account:
        result += f"{to_display}\n"

    # Форматируем валюту
    currency_display = "руб." if any(rub_word in currency.lower() for rub_word in ['руб', 'rub', 'rur']) else currency
    result += f"Сумма: {amount} {currency_display}"

    return result


def print_transactions(transactions: list):
    """Вывод списка транзакций"""
    if not transactions:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        return

    print(f"\nВсего банковских операций в выборке: {len(transactions)}\n")

    for i, transaction in enumerate(transactions, 1):
        formatted = format_transaction(transaction)
        print(formatted)
        if i < len(transactions):
            print()


def list_available_files():
    """Показать доступные файлы в папке data"""
    print(f"\nПроверяем папку: {DATA_DIR}")
    if DATA_DIR.exists():
        files = list(DATA_DIR.glob("*"))
        json_files = [f for f in files if f.suffix.lower() == '.json']
        csv_files = [f for f in files if f.suffix.lower() == '.csv']
        xlsx_files = [f for f in files if f.suffix.lower() == '.xlsx']

        if json_files:
            print("JSON файлы:")
            for file in json_files:
                print(f"   - {file.name}")

        if csv_files:
            print("CSV файлы:")
            for file in csv_files:
                print(f"   - {file.name}")

        if xlsx_files:
            print("XLSX файлы:")
            for file in xlsx_files:
                print(f"   - {file.name}")

        if not files:
            print("   (папка пуста)")
    else:
        print(f"Папка {DATA_DIR} не найдена")


def count_operations_by_status(transactions: list) -> dict:
    """Подсчет операций по статусам с использованием Counter"""
    if not transactions:
        return {}

    statuses = [tx.get('status', 'Без статуса') for tx in transactions]
    status_counter = Counter(statuses)
    return dict(status_counter.most_common())


# Основная функция
def main():
    """Основная функция приложения"""
    setup_logging()

    print("=" * 70)
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("=" * 70)

    try:
        # Показываем доступные файлы
        list_available_files()

        # Выбор типа файла
        file_types = [
            "Получить информацию о транзакциях из JSON-файла",
            "Получить информацию о транзакциях из CSV-файла",
            "Получить информацию о транзакций из XLSX-файла"
        ]

        file_choice = get_user_choice(file_types, "Выберите необходимый пункт меню:")

        # Загрузка данных
        if "JSON" in file_choice:
            transactions = load_transactions_from_json()
            print("Для обработки выбран JSON-файл.")
        elif "CSV" in file_choice:
            transactions = load_transactions_from_csv()
            print("Для обработки выбран CSV-файл.")
        else:
            transactions = load_transactions_from_xlsx()
            print("Для обработки выбран XLSX-файл.")

        if not transactions:
            print("Не удалось загрузить транзакции или файл пуст.")
            return

        print(f"Успешно загружено {len(transactions)} транзакций")

        # Получаем доступные статусы
        available_statuses = get_available_statuses(transactions)
        if not available_statuses:
            print("В файле не найдено транзакций с указанными статусами.")
            return

        # Фильтрация по статусу
        status = get_status_filter(available_statuses)
        filtered_transactions = filter_by_status(transactions, status)
        print(f"Операции отфильтрованы по статусу '{status}'")

        if not filtered_transactions:
            print("Не найдено транзакций с выбранным статусом.")
            return

        # Дополнительные фильтры
        current_transactions = filtered_transactions

        # Сортировка по дате
        if get_yes_no_input("Отсортировать операции по дате?"):
            sort_reverse = get_sort_direction()
            current_transactions = sort_by_date(current_transactions, sort_reverse)
            direction = "по убыванию" if sort_reverse else "по возрастанию"
            print(f"Операции отсортированы {direction}")

        # Фильтрация рублевых транзакций
        if get_yes_no_input("Выводить только рублевые транзакции?"):
            current_transactions = filter_rub_transactions(current_transactions)
            print("Выводятся только рублевые транзакции")

        # Поиск по описанию
        if get_yes_no_input("Отфильтровать список транзакций по определенному слову в описании?"):
            search_word = get_search_word()
            current_transactions = filter_by_description(current_transactions, search_word)
            print(f"Операции отфильтрованы по слову '{search_word}'")

        if not current_transactions:
            print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
            return

        # Статистика
        status_stats = count_operations_by_status(current_transactions)
        print(f"\nСтатистика по отфильтрованным данным:")
        print(f"   Всего операций: {len(current_transactions)}")
        if status_stats:
            print(f"   Распределение по статусам:")
            for status, count in status_stats.items():
                print(f"     - {status}: {count} операций")

        # Вывод результатов
        print("\nРаспечатываю итоговый список транзакций...")
        print_transactions(current_transactions)

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
