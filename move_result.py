from typing import ForwardRef, Optional


class MoveResult:
    def __init__(self, move_category: int, is_critical: Optional[bool] = False, type_effectiveness: Optional[float | int] = None,
                 stat_change_target: Optional[ForwardRef('Pokemon')] = None, stat_change_list: Optional[list] = None):
        self.move_category = move_category
        self.is_critical = is_critical
        self.type_effectiveness = type_effectiveness
        self.stat_change_target = stat_change_target
        self.stat_change_list = stat_change_list

    def set_damage_attack(self, is_critical: bool, type_effectiveness: float) -> 'MoveResult':
        self.is_critical = is_critical
        self.type_effectiveness = type_effectiveness
        return self

    def set_stat_change(self, stat_change_target: ForwardRef('Pokemon'), stat_change_list: list) -> 'MoveResult':
        self.stat_change_target = stat_change_target
        self.stat_change_list = stat_change_list
        return self
