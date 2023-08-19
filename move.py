from typing import Optional

import util


class Move:
    def __init__(self, move_id: int):
        self.id: int = move_id
        self.data: dict = util.fetch_json('move', str(move_id))

        self.accuracy: int = self.data['accuracy']
        self.damage_class: int = util.url_to_id(self.data['damage_class']['url'], 'move-damage-class')
        self.effect_chance: int = self.data['effect_chance']
        self.meta: dict = self.data['meta']
        self.ailment: int = util.url_to_id(self.meta['ailment']['url'], 'move-ailment')
        self.ailment_chance: int = self.meta['ailment_chance']
        self.category: int = util.url_to_id(self.meta['category']['url'], 'move-category')
        self.crit_rate: int = self.meta['crit_rate']
        self.drain: int = self.meta['drain']
        self.flinch_chance: int = self.meta['flinch_chance']
        self.healing: int = self.meta['healing']
        self.max_hits: Optional[int] = self.meta['max_hits']
        self.max_turns: Optional[int] = self.meta['max_turns']
        self.min_hits: Optional[int] = self.meta['min_hits']
        self.min_turns: Optional[int] = self.meta['min_turns']
        self.stat_chance: int = self.meta['stat_chance']
        self.name: str = self.data['name'].capitalize()
        self.power: int = self.data['power']
        self.pp: int = self.data['pp']
        self.max_pp: int = self.data['pp']
        self.priority: int = self.data['priority']
        self.stat_changes: list = [{'stat': util.url_to_id(x['stat']['url'], 'stat'), 'change': x['change']} for x in self.data['stat_changes']]
        self.move_target: int = util.url_to_id(self.data['target']['url'], 'move-target')
        self.type: int = util.url_to_id(self.data['type']['url'], 'type')
