import pandas as pd
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinancialDataReader:
    """Класс для считывания финансовых операций из CSV и XLSX файлов"""

    def __init__(self):
        self.transactions = []

    def read_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        Считывание данных из CSV файла

        Args:
            file_path (str): Путь к CSV файлу

        Returns:
            pd.DataFrame: DataFrame с транзакциями
        """
        try:
            logger.info(f"Чтение CSV файла: {file_path}")
            df = pd.read_csv(file_path, delimiter=';')
            logger.info(f"Успешно прочитано {len(df)} записей из CSV")
            return df
        except Exception as e:
            logger.error(f"Ошибка при чтении CSV файла: {e}")
            raise

    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        Считывание данных из XLSX файла

        Args:
            file_path (str): Путь к XLSX файлу

        Returns:
            pd.DataFrame: DataFrame с транзакциями
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

        Args:
            df (pd.DataFrame): DataFrame с сырыми данными
            source (str): Источник данных ('csv' или 'excel')

        Returns:
            list: Список обработанных транзакций
        """
        transactions = []

        for _, row in df.iterrows():
            try:
                transaction = {
                    'id': row['id'],
                    'state': row['state'],
                    'date': row['date'],
                    'amount': row['amount'],
                    'currency_name': row['currency_name'],
                    'currency_code': row['currency_code'],
                    'from_account': row.get('from', ''),
                    'to_account': row.get('to', ''),
                    'description': row['description'],
                    'source': source
                }
                transactions.append(transaction)
            except KeyError as e:
                logger.warning(f"Отсутствует поле в данных: {e}")
                continue
            except Exception as e:
                logger.warning(f"Ошибка обработки строки: {e}")
                continue

        return transactions

    def read_all_data(self, csv_path: str, excel_path: str) -> list:
        """
        Считывание данных из обоих файлов

        Args:
            csv_path (str): Путь к CSV файлу
            excel_path (str): Путь к XLSX файлу

        Returns:
            list: Объединенный список всех транзакций
        """
        all_transactions = []

        # Чтение CSV
        try:
            csv_df = self.read_csv_file(csv_path)
            csv_transactions = self.process_transactions(csv_df, 'csv')
            all_transactions.extend(csv_transactions)
            logger.info(f"Обработано {len(csv_transactions)} транзакций из CSV")
        except Exception as e:
            logger.error(f"Не удалось обработать CSV файл: {e}")

        # Чтение Excel
        try:
            excel_df = self.read_excel_file(excel_path)
            excel_transactions = self.process_transactions(excel_df, 'excel')
            all_transactions.extend(excel_transactions)
            logger.info(f"Обработано {len(excel_transactions)} транзакций из Excel")
        except Exception as e:
            logger.error(f"Не удалось обработать Excel файл: {e}")

        logger.info(f"Всего обработано {len(all_transactions)} транзакций")
        return all_transactions

    def display_transactions(self, transactions: list, limit: int = 5):
        """
        Отображение транзакций в удобном формате

        Args:
            transactions (list): Список транзакций
            limit (int): Количество транзакций для отображения
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


def main():
    """Основная функция для демонстрации работы"""
    reader = FinancialDataReader()

    try:
        # Считывание данных из обоих файлов
        all_transactions = reader.read_all_data(
            csv_path='transactions.csv',
            excel_path='transactions_excel.xlsx'
        )

        # Отображение результатов
        reader.display_transactions(all_transactions, limit=10)

        # Статистика
        print(f"\n{'=' * 50}")
        print("СТАТИСТИКА:")
        print(f"{'=' * 50}")

        states = {}
        currencies = {}
        sources = {}

        for transaction in all_transactions:
            states[transaction['state']] = states.get(transaction['state'], 0) + 1
            currencies[transaction['currency_code']] = currencies.get(transaction['currency_code'], 0) + 1
            sources[transaction['source']] = sources.get(transaction['source'], 0) + 1

        print(f"Всего транзакций: {len(all_transactions)}")
        print(f"По статусам: {states}")
        print(f"По валютам: {currencies}")
        print(f"По источникам: {sources}")

    except Exception as e:
        logger.error(f"Ошибка в основном процессе: {e}")


if __name__ == "__main__":
    main()
    