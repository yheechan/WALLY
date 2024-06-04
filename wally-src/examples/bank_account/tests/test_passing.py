import pytest
from bank_account import bank_account

@pytest.fixture
def bank():
    return  bank_account.create_bank()

def test_create_account(bank):
    create_account = bank
    _, _, _, get_balance = create_account("account1", 1000)
    assert get_balance() == 1000

def test_deposit(bank):
    create_account = bank
    deposit, _, _, get_balance = create_account("account1", 1000)
    deposit(500)
    assert get_balance() == 1500

def test_withdraw(bank):
    create_account = bank
    _, withdraw, _, get_balance = create_account("account1", 1000)
    withdraw(500)
    assert get_balance() == 500

def test_transfer(bank):
    create_account = bank
    account1 = create_account("account1", 1000)
    account2 = create_account("account2", 500)
    _, _, transfer_to, get_balance1 = account1
    _, _, _, get_balance2 = account2
    transfer_to("account2", 300)
    assert get_balance1() == 700
    assert get_balance2() == 800

def test_multiple_accounts(bank):
    create_account = bank
    create_account("account1", 1000)
    create_account("account2", 500)
    assert len(bank.__closure__[0].cell_contents) == 2  # Check if there are two accounts in the bank

import pytest
from bank_account import bank_account

@pytest.fixture
def bank():
    return bank_account.create_bank()

def test_create_duplicate_account(bank):
    create_account = bank
    create_account("account1", 1000)
    with pytest.raises(ValueError):
        create_account("account1", 500)  # This should raise an error due to duplicate account ID

def test_withdraw_more_than_balance(bank):
    create_account = bank
    _, withdraw, _, get_balance = create_account("account1", 1000)
    with pytest.raises(ValueError):
        withdraw(1500)  # This should raise an error due to insufficient funds

def test_transfer_more_than_balance(bank):
    create_account = bank
    account1 = create_account("account1", 1000)
    create_account("account2", 500)
    _, _, transfer_to, _ = account1
    with pytest.raises(ValueError):
        transfer_to("account2", 1500)  # This should raise an error due to insufficient funds



def test_create_multiple_accounts(bank):
    create_account = bank
    create_account("account1", 1000)
    create_account("account2", 500)
    with pytest.raises(ValueError):
        create_account("account1", 500)  # This should raise an error due to duplicate account ID
