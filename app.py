"""
Точка входа в приложение банковских транзакций
"""

import os
import sys

# Добавляем src в путь для импорта
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()
