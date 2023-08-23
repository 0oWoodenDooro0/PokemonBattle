from enum import Enum, auto


class BattleState(Enum):
    PREBATTLE = auto()
    SELECTION = auto()
    FIGHT = auto()
    ATTACK = auto()
    DEFEAT = auto()
    EXP = auto()


class AttackState(Enum):
    ATTACK = auto()
    ATTACK_HIT = auto()
    ATTACK_NOT_HIT = auto()
    CRICAL_HIT = auto()
    EFFECTIVE = auto()
    STAT_CHANGE = auto()
