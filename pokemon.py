import io
import math
import random
from urllib.request import urlopen

import pygame as pg

import constants as const
import util
from health_bar import HealthBar


class Pokemon:
    def __init__(self, data: dict, front: bool = False):
        self.data: dict = data
        self.front: bool = front
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
        self.level: int = 1
        self.health_bar: HealthBar | None = None
        self.set_sprite()
        self.set_pokemon_data()

    def set_pokemon_data(self):
        self.pokemon_id = self.data['id']
        self.name = self.data['name']

        self.types = [util.url_to_id(x['type']['url'], 'https://pokeapi.co/api/v2/type/') for x in self.data['types']]

        self.basic_stats = {}
        self.basic_points = {}
        self.stats_effect = {}
        for stat in self.data['stats']:
            stat_name = stat['stat']['name']
            self.basic_stats[stat_name] = stat['base_stat']
            self.basic_points[stat_name] = 0
            self.stats_effect[stat_name] = 0
        self.stats_effect['accuracy'] = 0
        self.stats_effect['evasion'] = 0

        self.individual_level = self.get_individual_level()

        self.stats = self.get_stat()

        self.hp = self.stats['hp']

        all_moves: list = self.data['moves']
        self.moves = []
        for move in all_moves:
            if move['version_group_details'][-1]['level_learned_at'] == 1 and move['version_group_details'][-1]['move_learn_method']['name'] == 'level-up' and \
                    move['version_group_details'][0]['version_group']['name'] == 'red-blue':
                move_id = util.url_to_id(move['move']['url'], 'https://pokeapi.co/api/v2/move/')
                data = util.fetch_json(f'move/{move_id}.json')
                move_data = {
                    'id': data['id'],
                    'name': data['name'],
                    'accuracy': data['accuracy'],
                    'effect_chance': data['effect_chance'],
                    'max_pp': data['pp'],
                    'pp': data['pp'],
                    'priority': data['priority'],
                    'power': data['power'],
                    'crit_rate': data['meta']['crit_rate'],
                    'type': util.url_to_id(data['type']['url'], 'https://pokeapi.co/api/v2/type/'),
                    'damage_class': util.url_to_id(data['damage_class']['url'], 'https://pokeapi.co/api/v2/move-damage-class/')
                }
                self.moves.append(move_data)

        if self.front:
            self.health_bar = HealthBar(const.POKEMON_IMAGE_SIZE // 2, const.POKEMON_IMAGE_SIZE // 4, 200, 20, self.stats["hp"])
        else:
            self.health_bar = HealthBar(const.SCREEN_WIDTH - const.POKEMON_IMAGE_SIZE // 2, const.SCREEN_HEIGHT - const.PANEL_HEIGHT - const.POKEMON_IMAGE_SIZE // 4, 200, 20,
                                        self.stats["hp"])

    @staticmethod
    def get_individual_level() -> dict:
        return {
            'hp': random.randint(0, 31),
            'attack': random.randint(0, 31),
            'defense': random.randint(0, 31),
            'speed': random.randint(0, 31),
            'special-attack': random.randint(0, 31),
            'special-defense': random.randint(0, 31)
        }

    def get_stat(self) -> dict:
        return {
            'hp': self.get_hp(),
            'attack': self.get_other_ability('attack'),
            'defense': self.get_other_ability('defense'),
            'speed': self.get_other_ability('speed'),
            'special_attack': self.get_other_ability('special-attack'),
            'special_defense': self.get_other_ability('special-defense'),
        }

    def get_hp(self) -> int:
        return math.floor(math.ceil(self.basic_stats['hp'] + self.individual_level['hp'] + math.sqrt(self.basic_points['hp']) / 8) * self.level / 50 + 10 + self.level)

    def get_other_ability(self, stat: str, character: int = 1) -> int:
        return math.floor(math.ceil(self.basic_stats[stat] + self.individual_level[stat] + math.sqrt(self.basic_points[stat]) / 8) * self.level / 50 + 5)

    def get_stat_effect(self, stat: str):
        level = self.stats_effect[stat]
        if level > 0:
            return math.floor((level + 2) / 2 * 100)
        elif level < 0:
            return math.floor(2 / (level + 2) * 100)
        else:
            return 1

    def set_sprite(self):
        image_url = self.data['sprites']['front_default'] if self.front else self.data['sprites']['back_default']
        image_stream = urlopen(image_url).read()
        image_file = io.BytesIO(image_stream)
        self.sprite = pg.image.load(image_file).convert_alpha()
        self.sprite = pg.transform.scale(self.sprite, (300, 300))
        self.sprite_rect = self.sprite.get_rect()
        if self.front:
            self.sprite_rect.topright = (const.SCREEN_WIDTH, - const.POKEMON_IMAGE_SIZE // 4)
        else:
            self.sprite_rect.bottomleft = (0, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + const.POKEMON_IMAGE_SIZE // 4)

    def draw(self, screen: pg.Surface):
        self.health_bar.draw(screen)
        screen.blit(self.sprite, self.sprite_rect)
        self.health_bar.update(self.hp)

    def attack(self, move: dict, defender_pokemon: 'Pokemon'):
        b = math.floor(move['accuracy'] * 255 / 100)
        c = self.get_stat_effect('accuracy')
        d = defender_pokemon.get_stat_effect('evasion')
        a = b * c / d
        r = random.randint(1, 255)
        if r < a and move['power']:
            if move['crit_rate'] > 0:
                crit = self.basic_stats['speed'] / 2
            else:
                crit = self.basic_stats['speed'] * 4
            r = random.randint(1, 256)
            critical = 1 if r > crit else 2
            power = move['power']
            attack = self.stats['attack'] if move['damage_class'] == 2 else self.stats['special-attack'] if move['damage_class'] == 3 else 0
            defense = defender_pokemon.stats['defense'] if move['damage_class'] == 2 else defender_pokemon.stats['special-attack'] if move['damage_class'] == 3 else 0
            move_type = move['type']
            stab = 1.5 if move_type in self.types else 1
            damage = (((2 * self.level * critical) / 5 + 2) * power * attack / defense / 50 + 2) * stab
            move_type_data = util.fetch_json(f'type/{move_type}.json')['damage_relations']
            for i in range(len(defender_pokemon.types)):
                if util.type_in_pokemon(move_type_data['double_damage_to'], defender_pokemon.types[i]):
                    damage = damage * 2
                elif util.type_in_pokemon(move_type_data['half_damage_to'], defender_pokemon.types[i]):
                    damage = damage * 0.5
                elif util.type_in_pokemon(move_type_data['no_damage_to'], defender_pokemon.types[i]):
                    damage = damage * 0
            damage = 1 if math.floor(damage) <= 1 else math.floor(damage * random.randint(217, 255) / 255)
            defender_pokemon.hp -= damage
        elif r < a:
            pass
        else:
            print(2)
