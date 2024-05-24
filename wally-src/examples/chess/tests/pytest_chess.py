import pytest
from chess import knight, rook, pawn

def test_knight_00():
    assert(knight.knight_frontright(1, 1) == (2, 3))

# failing test for knight
def test_knight_01():
    assert(knight.knight_frontright(1, 2) == (2, 3))

def test_rook_00():
    assert(rook.rook_right(1, 1) == (2, 1))

# failing test for rook
def test_rook_01():
    assert(rook.rook_right(1, 1) == (2, 2))

def test_pawn_00():
    assert(pawn.pawn_front(1, 1) == (1, 2))

# failing test for pawn
def test_pawn_01():
    assert(pawn.pawn_front(1, 1) == (1, 3))
