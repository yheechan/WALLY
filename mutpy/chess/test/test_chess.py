from unittest import TestCase
from chess import knight, rook, pawn

class ChessTest(TestCase):
    def test_knight_00(self):
        self.assertEqual(knight.knight_frontright(1, 1), (2, 3))

    # failing test for knight
    def test_knight_01(self):
        self.assertEqual(knight.knight_frontright(1, 1), (3, 3))

    def test_rook_00(self):
        self.assertEqual(rook.rook_right(1, 1), (2, 1))

    # failing test for rook
    def test_rook_01(self):
        self.assertEqual(rook.rook_right(1, 1), (2, 2))

    def test_pawn_00(self):
        self.assertEqual(pawn.pawn_front(1, 1), (1, 2))
    
    # failing test for pawn
    def test_pawn_01(self):
        self.assertEqual(pawn.pawn_front(1, 1), (1, 3))
