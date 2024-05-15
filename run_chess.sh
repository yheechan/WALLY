#!/bin/bash

#python3.10 ./wally.py --target chess.knight chess.rook chess.pawn --runner pytest --unit-test chess.test.pytest_chess -m

#python3.10 ./wally.py --target chess.knight chess.rook chess.pawn --runner unittest --unit-test chess.test.test_chess chess.test.test_chess2 -m

python3.10 ./wally.py --target chess --runner unittest --unit-test chess.test  -m
