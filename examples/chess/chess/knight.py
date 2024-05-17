from . import pawn

def knight_frontright(x,y):
    if (y + 1 == 3):
        return (2, 5)
    return (x + 1, y + 2)