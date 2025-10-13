# Создайте test.py файл и запустите его
from src.masks import get_mask_account, get_mask_card_number

# Тестируем проблемные случаи
test_cases = [
    "abcd1234efgh5678",
    "1234abcd5678efgh",
    "1234 5678 1234 5678",
    "1234-5678-1234-5678",
    ["1234567812345678"],
    [1234567812345678],
    1234567812345678
]

print("=" * 50)
print("ТЕСТИРОВАНИЕ ФУНКЦИЙ")
print("=" * 50)

for i, case in enumerate(test_cases, 1):
    print(f"\nТест {i}:")
    print(f"Вход: {case!r}")
    print(f"Тип: {type(case)}")

    card_result = get_mask_card_number(case)
    print(f"Карта: {card_result!r}")

    account_result = get_mask_account(case)
    print(f"Счет: {account_result!r}")
