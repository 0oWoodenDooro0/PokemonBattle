class AttackResult:
    def __init__(self, move_category: int, is_critical: bool = False, type_effectiveness: float = None, stat_change_target: 'Pokemon' = None, stat_change_list: list = None):
        self.move_category = move_category
        self.is_critical = is_critical
        self.type_effectiveness = type_effectiveness
        self.stat_change_target = stat_change_target
        self.stat_change_list = stat_change_list

    def set_damage_attack(self, is_critical: bool = False, type_effectiveness: float = None):
        self.is_critical = is_critical
        self.type_effectiveness = type_effectiveness
        return self

    def set_stat_change(self, stat_change_target: 'Pokemon' = None, stat_change_list: list = None):
        self.stat_change_target = stat_change_target
        self.stat_change_list = stat_change_list
        return self
