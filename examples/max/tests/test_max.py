import pytest
from max import find_max  # Ensure this import matches your actual module/file setup.

def test_find_max01():
    assert find_max([1, 3, 2]) == 3

def test_find_max02():
    assert find_max([-1, -3, -2]) == -1

def test_find_max03():
    assert find_max([1, 1, 1]) == 1

def test_find_max04():
    assert find_max([-10, -10, -10]) == -10

def test_find_max05():
    assert find_max([0, 0, 0]) == 0

def test_find_max06():
    assert find_max([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 10

def test_find_max07():
    assert find_max([-1, -2, -3, -4, -5, -6, -7, -8, -9, -10]) == -1

def test_find_max08():
    assert find_max([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0]) == 10

def test_find_max09():
    assert find_max([0, 0, 0, 0, -1, 100, 10, 10, 10, 10]) == 100
