import pandas as pd
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


logger = setup_logger('financial_reader', force_recreate=True)


class FinancialDataReader:
    """Класс для считывания финансовых операций из CSV и XLSX файлов"""

    def __init__(self):
        self.transactions = []

    def read_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        Считывание данных из CSV файла с обработкой кодировки
        """
        try:
            logger.info(f"Чтение CSV файла: {file_path}")

            # Пробуем разные кодировки
            encodings = ['utf-8', 'cp1251', 'latin1']

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, delimiter=';', encoding=encoding)
                    logger.info(f"Успешно прочитано {len(df)} записей из CSV с кодировкой {encoding}")
                    return df
                except UnicodeDecodeError:
                    continue

            # Если ни одна кодировка не подошла
            raise UnicodeDecodeError("Не удалось определить кодировку файла")

        except Exception as e:
            logger.error(f"Ошибка при чтении CSV файла: {e}")
            raise

    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        Считывание данных из XLSX файла
        """
        try:
            logger.info(f"Чтение Excel файла: {file_path}")
            df = pd.read_excel(file_path)
            logger.info(f"Успешно прочитано {len(df)} записей из Excel")
            return df
        except Exception as e:
            logger.error(f"Ошибка при чтении Excel файла: {e}")
            raise

    def process_transactions(self, df: pd.DataFrame, source: str) -> list:
        """
        Обработка и преобразование данных транзакций
        """
        transactions = []

        for _, row in df.iterrows():
            try:
                transaction = {
                    'id': row['id'],
                    'state': row['state'],
                    'date': row['date'],
                    'amount': float(row['amount']),
                    'currency_name': row['currency_name'],
                    'currency_code': row['currency_code'],
                    'from_account': row.get('from', ''),
                    'to_account': row.get('to', ''),
                    'description': row['description'],
                    'source': source
                }
                transactions.append(transaction)
            except Exception as e:
                logger.warning(f"Ошибка обработки строки: {e}")
                continue

        return transactions


def display_transactions(transactions: list, limit: int = 5):
    """
    Отображение транзакций в удобном формате
    """
    print(f"\n{'=' * 80}")
    print(f"ФИНАНСОВЫЕ ОПЕРАЦИИ (первые {limit} из {len(transactions)})")
    print(f"{'=' * 80}")

    for i, transaction in enumerate(transactions[:limit]):
        print(f"\n--- Транзакция {i + 1} ---")
        print(f"ID: {transaction['id']}")
        print(f"Статус: {transaction['state']}")
        print(f"Дата: {transaction['date']}")
        print(f"Сумма: {transaction['amount']} {transaction['currency_name']} ({transaction['currency_code']})")
        print(f"Откуда: {transaction['from_account']}")
        print(f"Куда: {transaction['to_account']}")
        print(f"Описание: {transaction['description']}")
        print(f"Источник: {transaction['source']}")
