import util


class Move:
    def __init__(self, move_id: int):
        self.id = move_id
        self.data = util.fetch_json('move', str(move_id))
        self.name = self.data['name'].capitalize()
        self.accuracy = self.data['accuracy']
        self.effect_chance = self.data['effect_chance']
        self.pp = self.data['pp']
        self.max_pp = self.data['pp']
        self.priority = self.data['priority']
        self.power = self.data['power']
        self.crit_rate = self.data['meta']['crit_rate']
        self.stat_changes = [{'stat': util.url_to_id(x['stat']['url'], 'stat'), 'change': x['change']} for x in self.data['stat_changes']]
        self.type = util.url_to_id(self.data['type']['url'], 'type')
        self.damage_class = util.url_to_id(self.data['damage_class']['url'], 'move-damage-class')
        self.move_target = util.url_to_id(self.data['target']['url'], 'move-target')
