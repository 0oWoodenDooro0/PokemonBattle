from enum import Enum, auto


class BattleState(Enum):
    PREBATTLE = auto()
    FIGHT = auto()
    ATTACK = auto()


class AttackState(Enum):
    FIRST_ATTACK = auto()
    FIRST_ATTACK_HIT = auto()
    FIRST_ATTACK_NOT_HIT = auto()
    FIRST_EFFECTIVE = auto()
    FIRST_STAT_CHANGE = auto()
    LAST_ATTACK = auto()
    LAST_ATTACK_HIT = auto()
    LAST_ATTACK_NOT_HIT = auto()
    LAST_EFFECTIVE = auto()
    LAST_STAT_CHANGE = auto()
