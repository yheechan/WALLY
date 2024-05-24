import pytest
from maxify import maxify  # Ensure this import matches your actual module/file setup.

def test_maxify_01():
    assert maxify.maxify([1, 3, 2]) == 3

def test_maxify_02():
    assert maxify.maxify([-1, -3, -2]) == -1

def test_maxify_03():
    assert maxify.maxify([1, 1, 1]) == 1

def test_maxify_04():
    assert maxify.maxify([-10, -10, -10]) == -10

def test_maxify_05():
    assert maxify.maxify([0, 0, 0]) == 0

def test_maxify_06():
    assert maxify.maxify([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == 10

def test_maxify_07():
    assert maxify.maxify([-1, -2, -3, -4, -5, -6, -7, -8, -9, -10]) == -1

def test_maxify_08():
    assert maxify.maxify([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0]) == 10

def test_maxify_09():
    assert maxify.maxify([0, 0, 0, 0, -1, 100, 10, 10, 10, 10]) == 100
