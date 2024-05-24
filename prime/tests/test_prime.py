import pytest
from prime import prime

def test_prime_00():
    assert(prime.prime(5) == [2, 3, 5, 7, 11])

def test_prime_01():
    assert(prime.prime(10) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

def test_prime_02():
    assert(prime.prime(1) == [2])

def test_prime_03():
    assert(prime.prime(2) == [2, 3])
