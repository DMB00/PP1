import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from masks import mask_card_number, mask_account_number


def test_mask_card_number_edge_cases():
    """Тест маскировки карты с граничными случаями"""
    assert mask_card_number(None) == ""
    assert mask_card_number("") == ""
    assert mask_card_number("1234") == "1234"
    assert mask_card_number("1234567890123456") == "1234 56** **** 3456"


def test_mask_account_number_edge_cases():
    """Тест маскировки счета с граничными случаями"""
    assert mask_account_number(None) == ""
    assert mask_account_number("") == ""
    assert mask_account_number("123") == "123"
    assert mask_account_number("1234567890") == "Счет **7890"


def test_mask_functions_consistency():
    """Тест согласованности функций маскировки"""
    # Карты должны маскироваться одинаково
    card1 = mask_card_number("1234567812345678")
    card2 = mask_card_number("1234567812345678")
    assert card1 == card2

    # Счета должны маскироваться одинаково
    account1 = mask_account_number("12345678901234567890")
    account2 = mask_account_number("12345678901234567890")
    assert account1 == account2
