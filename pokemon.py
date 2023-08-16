import io
import math
import random
from urllib.request import urlopen

import pygame as pg

import constants as const
import util
from health_bar import HealthBar


class Pokemon:
    def __init__(self, data: dict, enemy: bool = False):
        self.data: dict = data
        self.enemy: bool = enemy
        self.sprite: pg.Surface | None = None
        self.sprite_rect: pg.Rect | None = None
        self.pokemon_id: int | None = None
        self.name: str | None = None
        self.basic_stats: dict | None = None
        self.individual_level: dict | None = None
        self.basic_points: dict | None = None
        self.stats: dict | None = None
        self.stats_effect: dict | None = None
        self.hp: int | None = None
        self.types: list | None = None
        self.moves: list | None = None
        self.pokemon_species: int | None = None
        self.base_experience: int | None = None
        self.experience: int = 0
        self.level: int = 1
        self.levels: list | None = None
        self.health_bar: HealthBar | None = None
        self.set_sprite()
        self.set_pokemon_data()

    def set_pokemon_data(self):
        self.pokemon_id = self.data['id']
        self.name = self.data['name'].capitalize()

        self.types = [util.url_to_id(x['type']['url'], 'https://pokeapi.co/api/v2/type/') for x in self.data['types']]

        self.basic_stats = {}
        self.basic_points = {}
        self.stats_effect = {}
        for stat in self.data['stats']:
            stat_id = util.url_to_id(stat['stat']['url'], 'https://pokeapi.co/api/v2/stat/')
            self.basic_stats[stat_id] = stat['base_stat']
            self.basic_points[stat_id] = 0
            self.stats_effect[stat_id] = 0
        self.stats_effect[7] = 0
        self.stats_effect[8] = 0

        self.individual_level = self.get_individual_level()

        self.stats = self.get_stat()

        self.hp = self.stats[1]

        all_moves: list = self.data['moves']
        self.moves = []
        for move in all_moves:
            if move['version_group_details'][-1]['level_learned_at'] == 1 and move['version_group_details'][-1]['move_learn_method']['name'] == 'level-up' and \
                    move['version_group_details'][0]['version_group']['name'] == 'red-blue':
                move_id = util.url_to_id(move['move']['url'], 'https://pokeapi.co/api/v2/move/')
                data = util.fetch_json(f'move/{move_id}.json')
                move_data = {
                    'id': data['id'],
                    'name': data['name'].capitalize(),
                    'accuracy': data['accuracy'],
                    'effect_chance': data['effect_chance'],
                    'max_pp': data['pp'],
                    'pp': data['pp'],
                    'priority': data['priority'],
                    'power': data['power'],
                    'crit_rate': data['meta']['crit_rate'],
                    'stat_changes': [{'stat': util.url_to_id(x['stat']['url'], 'https://pokeapi.co/api/v2/stat/'), 'change': x['change']} for x in data['stat_changes']],
                    'type': util.url_to_id(data['type']['url'], 'https://pokeapi.co/api/v2/type/'),
                    'damage_class': util.url_to_id(data['damage_class']['url'], 'https://pokeapi.co/api/v2/move-damage-class/'),
                    'move_target': util.url_to_id(data['target']['url'], 'https://pokeapi.co/api/v2/move-target/')
                }
                self.moves.append(move_data)

        self.pokemon_species = util.url_to_id(self.data['species']['url'], 'https://pokeapi.co/api/v2/pokemon-species/')

        self.base_experience = self.data['base_experience']

        self.levels = self.get_grow_rate()

        if self.enemy:
            self.health_bar = HealthBar(const.POKEMON_IMAGE_SIZE // 2, const.POKEMON_IMAGE_SIZE // 4, 200, 20, self.stats[1])
        else:
            self.health_bar = HealthBar(const.SCREEN_WIDTH - const.POKEMON_IMAGE_SIZE // 2, const.SCREEN_HEIGHT - const.PANEL_HEIGHT - const.POKEMON_IMAGE_SIZE // 4, 200, 20,
                                        self.stats[1])

    def get_grow_rate(self) -> list:
        for i in range(6):
            grow_rate_data = util.fetch_json(f'growth-rate/{i + 1}.json')
            species_list = grow_rate_data['pokemon_species']
            for species in species_list:
                species_id = util.url_to_id(species['url'], 'https://pokeapi.co/api/v2/pokemon-species/')
                if species_id > self.pokemon_species:
                    break
                if species_id == self.pokemon_species:
                    return grow_rate_data['levels']

    @staticmethod
    def get_individual_level() -> dict:
        return {
            1: random.randint(0, 31),
            2: random.randint(0, 31),
            3: random.randint(0, 31),
            4: random.randint(0, 31),
            5: random.randint(0, 31),
            6: random.randint(0, 31)
        }

    def get_stat(self) -> dict:
        return {
            1: self.get_hp(),
            2: self.get_other_ability(2),
            3: self.get_other_ability(3),
            4: self.get_other_ability(4),
            5: self.get_other_ability(5),
            6: self.get_other_ability(6),
        }

    def get_hp(self) -> int:
        return math.floor(math.ceil(self.basic_stats[1] + self.individual_level[1] + math.sqrt(self.basic_points[1]) / 8) * self.level / 50 + 10 + self.level)

    def get_other_ability(self, stat_id: int) -> int:
        return math.floor(math.ceil(self.basic_stats[stat_id] + self.individual_level[stat_id] + math.sqrt(self.basic_points[stat_id]) / 8) * self.level / 50 + 5)

    def get_stat_effect(self, stat_id: int):
        level = self.stats_effect[stat_id]
        if level > 0:
            return math.floor((level + 2) / 2 * 100) / 100
        elif level < 0:
            return math.floor(2 / (abs(level) + 2) * 100) / 100
        else:
            return 1

    def set_sprite(self):
        image_url = self.data['sprites']['front_default'] if self.enemy else self.data['sprites']['back_default']
        image_stream = urlopen(image_url).read()
        image_file = io.BytesIO(image_stream)
        self.sprite = pg.image.load(image_file).convert_alpha()
        self.sprite = pg.transform.scale(self.sprite, (300, 300))
        self.sprite_rect = self.sprite.get_rect()
        if self.enemy:
            self.sprite_rect.topright = (const.SCREEN_WIDTH, - const.POKEMON_IMAGE_SIZE // 4)
        else:
            self.sprite_rect.bottomleft = (0, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + const.POKEMON_IMAGE_SIZE // 4)

    def draw(self, screen: pg.Surface):
        self.health_bar.draw(screen)
        screen.blit(self.sprite, self.sprite_rect)
        if self.hp < 0:
            self.hp = 0
        self.health_bar.update(self.hp)

    def attack(self, move: dict, defender_pokemon: 'Pokemon'):
        critical: int | None = None
        type_effectiveness: int | float | list | None = None
        if move['damage_class'] != 1:
            if move['crit_rate'] == 0:
                crit = self.basic_stats[6] / 2
            else:
                crit = self.basic_stats[6] * 4
            r = random.randint(1, 256)
            critical = 1 if r > crit else 2
            power = move['power']
            attack_stat = self.stats[2] if move['damage_class'] == 2 else self.stats[4] if move['damage_class'] == 3 else 0
            attack = attack_stat * self.get_stat_effect(2)
            defense_stat = defender_pokemon.stats[3] if move['damage_class'] == 2 else defender_pokemon.stats[5] if move['damage_class'] == 3 else 0
            defense = defense_stat * self.get_stat_effect(3)
            move_type = move['type']
            stab = 1.5 if move_type in self.types else 1
            damage = (((2 * self.level * critical) / 5 + 2) * power * attack / defense / 50 + 2) * stab
            move_type_data = util.fetch_json(f'type/{move_type}.json')['damage_relations']
            type_effectiveness = 1
            for i in range(len(defender_pokemon.types)):
                if util.type_in_pokemon(move_type_data['double_damage_to'], defender_pokemon.types[i]):
                    damage = damage * 2
                    type_effectiveness = type_effectiveness * 2
                elif util.type_in_pokemon(move_type_data['half_damage_to'], defender_pokemon.types[i]):
                    damage = damage * 0.5
                    type_effectiveness = type_effectiveness * 0.5
                elif util.type_in_pokemon(move_type_data['no_damage_to'], defender_pokemon.types[i]):
                    damage = damage * 0
                    type_effectiveness = type_effectiveness * 0
            damage = 1 if math.floor(damage) <= 1 else math.floor(damage * random.randint(217, 255) / 255)
            defender_pokemon.hp -= damage
        stat_change_list = []
        if move['damage_class'] == 1:
            for i in range(len(move['stat_changes'])):
                target_pokemon: Pokemon | None = None
                match move['move_target']:
                    case 10 | 11:
                        target_pokemon = defender_pokemon
                    case 7:
                        target_pokemon = self
                    case _:
                        print(move['move_target'])
                stat_change = 0
                if move['stat_changes'][i]['change'] > 0 and target_pokemon.stats_effect[move['stat_changes'][i]['stat']] == 6:
                    stat_change = 9
                elif move['stat_changes'][i]['change'] < 0 and target_pokemon.stats_effect[move['stat_changes'][i]['stat']] == -6:
                    stat_change = 10
                elif target_pokemon.stats_effect[move['stat_changes'][i]['stat']] + move['stat_changes'][i]['change'] >= 6:
                    target_pokemon.stats_effect[move['stat_changes'][i]['stat']] = 6
                    stat_change = 4
                else:
                    target_pokemon.stats_effect[move['stat_changes'][i]['stat']] += move['stat_changes'][i]['change']
                    if target_pokemon.stats_effect[move['stat_changes'][i]['stat']] > 6:
                        target_pokemon.stats_effect[move['stat_changes'][i]['stat']] = 6
                    elif target_pokemon.stats_effect[move['stat_changes'][i]['stat']] < -6:
                        target_pokemon.stats_effect[move['stat_changes'][i]['stat']] = -6
                    match move['stat_changes'][i]['change']:
                        case 1:
                            stat_change = 1
                        case 2:
                            stat_change = 2
                        case 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11:
                            stat_change = 3
                        case -1:
                            stat_change = 6
                        case -2:
                            stat_change = 7
                        case -3 | -4 | -5 | -6 | -7 | -8 | -9 | -10 | -11:
                            stat_change = 8
                        case _:
                            print(move['stat_changes'])
                stat_name = util.fetch_json(f'stat/{move["stat_changes"][i]["stat"]}.json')
                stat_change_list.append((target_pokemon, stat_name['name'], stat_change))
        move['pp'] -= 1
        return critical, type_effectiveness, stat_change_list

    def attack_accuracy(self, move: dict, defender_pokemon: 'Pokemon'):
        b = math.floor(move['accuracy'] * 255 / 100)
        c = self.get_stat_effect(7)
        d = defender_pokemon.get_stat_effect(8)
        a = b * c / d
        r = random.randint(1, 255)
        return True if r < a else False

    def add_experience(self, experience: int):
        self.experience += experience
        self.check_experience_to_level_up()

    def check_experience_to_level_up(self):
        if self.level == 100:
            return
        if self.experience < self.levels[self.level + 1]['experience']:
            self.level += 1
            self.check_experience_to_level_up()
