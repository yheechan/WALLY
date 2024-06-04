import pytest
from bank_account import bank_account

@pytest.fixture
def bank():
    return  bank_account.create_bank()

def test_withdraw_equal_balance(bank):
    create_account = bank
    _, withdraw, _, get_balance = create_account("account1", 1000)
    # This  raise an error because withdrawing equal to balance should not be allowed due to the bug
    withdraw(1000)

def test_withdraw_equal_balance_2(bank):
    create_account = bank
    _, withdraw, _, get_balance = create_account("account1", 300)
    # This  raise an error because withdrawing equal to balance should not be allowed due to the bug
    withdraw(300)