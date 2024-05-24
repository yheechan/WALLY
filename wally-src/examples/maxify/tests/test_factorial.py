import pytest
from maxify import factorial

def test_factorial_zero():
    assert factorial.factorial(0) == 1

def test_factorial_one():
    assert factorial.factorial(3) == 6

def test_factorial_five():
    assert factorial.factorial(5) == 120

def test_factorial_ten():
    assert factorial.factorial(10) == 3628800