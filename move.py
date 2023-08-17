import util


class Move:
    def __init__(self, move_id: int):
        self.id = move_id
        self.data = util.fetch_json('move', str(move_id))

        self.accuracy = self.data['accuracy']
        self.damage_class = util.url_to_id(self.data['damage_class']['url'], 'move-damage-class')
        self.effect_chance = self.data['effect_chance']
        self.meta = self.data['meta']
        self.ailment = util.url_to_id(self.meta['aliment']['url'], 'move-ailment')
        self.ailment_chance = self.meta['ailment_chance']
        self.category = self.meta['category']
        self.crit_rate = self.meta['crit_rate']
        self.drain = self.meta['drain']
        self.flinch_chance = self.meta['flinch_chance']
        self.healing = self.meta['healing']
        self.max_hits = self.meta['max_hits']
        self.max_turns = self.meta['max_turns']
        self.min_hits = self.meta['min_hits']
        self.min_turns = self.meta['min_turns']
        self.stat_chance = self.meta['stat_chance']
        self.name = self.data['name'].capitalize()
        self.power = self.data['power']
        self.pp = self.data['pp']
        self.max_pp = self.data['pp']
        self.priority = self.data['priority']
        self.stat_changes = [{'stat': util.url_to_id(x['stat']['url'], 'stat'), 'change': x['change']} for x in self.data['stat_changes']]
        self.move_target = util.url_to_id(self.data['target']['url'], 'move-target')
        self.type = util.url_to_id(self.data['type']['url'], 'type')
