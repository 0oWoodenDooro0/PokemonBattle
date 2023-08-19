import io
import math
import random
from urllib.request import urlopen

import pygame as pg

import constants as const
import util
from attack_result import AttackResult
from generation import Generation
from health_bar import HealthBar
from move import Move


class Pokemon:
    def __init__(self, pokemon_id: int, generation: Generation, enemy: bool = False):
        self.generation = generation
        self.id: int = pokemon_id
        self.data: dict = util.fetch_json('pokemon', str(pokemon_id))
        self.enemy: bool = enemy
        self.base_experience: int = self.data['base_experience']
        self.experience: int = 0
        self.level: int = 1
        self.moves: list[Move] = self.get_moves()
        self.name: str = self.data['name'].capitalize()
        self.species: int = util.url_to_id(self.data['species']['url'], 'pokemon-species')
        self.levels: list = self.get_levels()
        sprite, sprite_rect = self.get_sprite()
        self.sprite: pg.Surface = sprite
        self.sprite_rect: pg.Rect = sprite_rect
        self.basic_stats: dict = self.get_basic_stats()
        self.individual_level: dict = self.get_individual_level()
        self.basic_points: dict = self.get_basic_point()
        self.stats: dict = self.get_stat()
        self.stats_effect: dict = self.reset_stats_effect()
        self.hp: int = self.stats[1]
        self.health_bar: HealthBar = self.get_health_bar()
        self.types: list[int] = [util.url_to_id(x['type']['url'], 'type') for x in self.data['types']]

    def set_pokemon_data(self):
        self.basic_stats = {}
        self.basic_points = {}
        self.stats_effect = {}
        for stat in self.data['stats']:
            stat_id = util.url_to_id(stat['stat']['url'], 'stat')
            self.basic_stats[stat_id] = stat['base_stat']
            self.basic_points[stat_id] = 0
            self.stats_effect[stat_id] = 0
        self.stats_effect[7] = 0
        self.stats_effect[8] = 0

    def get_basic_stats(self):
        return {util.url_to_id(stat['stat']['url'], 'stat'): stat['base_stat'] for stat in self.data['stats']}

    @staticmethod
    def get_basic_point():
        return {i + 1: 0 for i in range(6)}

    @staticmethod
    def reset_stats_effect():
        return {i + 1: 0 for i in range(8)}

    def get_moves(self):
        move_list: list = self.data['moves']
        moves = []
        for move in move_list:
            move_id = util.url_to_id(move['move']['url'], 'move')
            if move_id in self.generation.moves and len(moves) < 4:
                move_id = util.url_to_id(move['move']['url'], 'move')
                move = Move(move_id)
                if move.category in [0, 2, 3, 6, 8, 9]:
                    moves.append(move)
        return moves

    def get_health_bar(self):
        if self.enemy:
            return HealthBar(const.POKEMON_IMAGE_SIZE // 2, const.POKEMON_IMAGE_SIZE // 4, 200, 20, self.stats[1])
        else:
            return HealthBar(const.SCREEN_WIDTH - const.POKEMON_IMAGE_SIZE // 2, const.SCREEN_HEIGHT - const.PANEL_HEIGHT - const.POKEMON_IMAGE_SIZE // 4, 200, 20,
                             self.stats[1])

    def get_levels(self) -> list:
        species_data = util.fetch_json('pokemon-species', str(self.species))
        growth_rate_id = util.url_to_id(species_data['growth_rate']['url'], 'growth-rate')
        growth_rate_data = util.fetch_json('growth-rate', str(growth_rate_id))
        return growth_rate_data['levels']

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

    def get_sprite(self):
        image_url = self.data['sprites']['front_default'] if self.enemy else self.data['sprites']['back_default']
        image_stream = urlopen(image_url).read()
        image_file = io.BytesIO(image_stream)
        sprite = pg.image.load(image_file).convert_alpha()
        sprite = pg.transform.scale(sprite, (300, 300))
        sprite_rect = sprite.get_rect()
        if self.enemy:
            sprite_rect.topright = (0, - const.POKEMON_IMAGE_SIZE // 5)
            return sprite, sprite_rect
        else:
            sprite_rect.bottomleft = (const.SCREEN_WIDTH, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + const.POKEMON_IMAGE_SIZE // 5)
            return sprite, sprite_rect

    def draw(self, screen: pg.Surface):
        screen.blit(self.sprite, self.sprite_rect)

    def draw_health_bar(self, screen):
        self.health_bar.draw(screen)
        if self.hp < 0:
            self.hp = 0
        self.health_bar.update(self.hp)

    def attack(self, move: Move, defender_pokemon: 'Pokemon'):
        print(f'{move.category=}')
        match move.category:
            case 0:
                attack_result, damage = self.damage_attack(move, defender_pokemon)
                defender_pokemon.hp -= damage
                return attack_result
            case 2:
                print(f'{move.stat_chance=}')
                match move.move_target:
                    case 10 | 11:
                        return self.stat_change(move, defender_pokemon)
                    case 7:
                        return self.stat_change(move, self)
                    case _:
                        print(move.move_target)
            case 3:
                self.hp += math.floor(move.healing / 100 * self.stats[1])
                if self.hp > self.stats[1]:
                    self.hp = self.stats[1]
                return AttackResult(3)
            case 6:
                attack_result, damage = self.damage_attack(move, defender_pokemon)
                defender_pokemon.hp -= damage
                if self.stat_accuracy(move.stat_chance):
                    return self.stat_change(move, defender_pokemon, attack_result)
                return attack_result
            case 7:
                attack_result, damage = self.damage_attack(move, defender_pokemon)
                defender_pokemon.hp -= damage
                if self.stat_accuracy(move.stat_chance):
                    return self.stat_change(move, self, attack_result)
                return attack_result
            case 8:
                attack_result, damage = self.damage_attack(move, defender_pokemon)
                defender_pokemon.hp -= damage
                self.hp += math.floor(move.drain / 100 * damage)
                if self.hp > self.stats[1]:
                    self.hp = self.stats[1]
                return attack_result
            case 9:
                defender_pokemon.hp = 0
                return AttackResult(9)
            case _:
                print(move.category)

    def damage_attack(self, move: Move, defender_pokemon: 'Pokemon', attack_result: AttackResult = None):
        if move.crit_rate == 0:
            crit = self.basic_stats[6] / 2
        else:
            crit = self.basic_stats[6] * 4
        r = random.randint(1, 256)
        critical = 1 if r > crit else 2
        power = move.power
        attack_stat = self.stats[2] if move.damage_class == 2 else self.stats[4] if move.damage_class == 3 else 0
        attack = attack_stat * self.get_stat_effect(2)
        defense_stat = defender_pokemon.stats[3] if move.damage_class == 2 else defender_pokemon.stats[5] if move.damage_class == 3 else 0
        defense = defense_stat * self.get_stat_effect(3)
        move_type = move.type
        stab = 1.5 if move_type in self.types else 1
        damage = (((2 * self.level * critical) / 5 + 2) * power * attack / defense / 50 + 2) * stab
        move_type_data = util.fetch_json('type', str(move_type))['damage_relations']
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
        if attack_result:
            attack_result.set_damage_attack(is_critical=True if critical == 2 else False, type_effectiveness=type_effectiveness)
        return AttackResult(move.category, is_critical=True if critical == 2 else False, type_effectiveness=type_effectiveness), damage

    @staticmethod
    def stat_change(move: Move, target_pokemon: 'Pokemon', attack_result: AttackResult = None):
        stat_change_list = []
        for i in range(len(move.stat_changes)):
            stat_change = 0
            if move.stat_changes[i]['change'] > 0 and target_pokemon.stats_effect[move.stat_changes[i]['stat']] == 6:
                stat_change = 9
            elif move.stat_changes[i]['change'] < 0 and target_pokemon.stats_effect[move.stat_changes[i]['stat']] == -6:
                stat_change = 10
            elif target_pokemon.stats_effect[move.stat_changes[i]['stat']] + move.stat_changes[i]['change'] >= 6:
                target_pokemon.stats_effect[move.stat_changes[i]['stat']] = 6
                stat_change = 4
            else:
                target_pokemon.stats_effect[move.stat_changes[i]['stat']] += move.stat_changes[i]['change']
                if target_pokemon.stats_effect[move.stat_changes[i]['stat']] > 6:
                    target_pokemon.stats_effect[move.stat_changes[i]['stat']] = 6
                elif target_pokemon.stats_effect[move.stat_changes[i]['stat']] < -6:
                    target_pokemon.stats_effect[move.stat_changes[i]['stat']] = -6
                match move.stat_changes[i]['change']:
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
                        print(move.stat_changes)
            stat_name = util.fetch_json('stat', str(move.stat_changes[i]["stat"]))
            stat_change_list.append((stat_name['name'].upper(), stat_change))
        if attack_result:
            attack_result.set_stat_change(stat_change_target=target_pokemon, stat_change_list=stat_change_list)
        return AttackResult(move.category, stat_change_target=target_pokemon, stat_change_list=stat_change_list)

    @staticmethod
    def stat_accuracy(stat_chance: int):
        if stat_chance == 0:
            return True
        r = random.randint(1, 100)
        return True if r <= stat_chance else False

    def attack_accuracy(self, move: Move, defender_pokemon: 'Pokemon'):
        if not move.accuracy:
            return True
        b = math.floor(move.accuracy * 255 / 100)
        c = self.get_stat_effect(7)
        d = defender_pokemon.get_stat_effect(8)
        a = b * c / d
        r = random.randint(1, 255)
        if move.category == 9:
            return True if r < b else False
        return True if r < a else False

    def add_experience(self, experience: int):
        self.experience += experience
        self.check_experience_to_level_up()

    def check_experience_to_level_up(self):
        if self.level == 100:
            return
        if self.experience >= self.levels[self.level + 1]['experience']:
            self.level += 1
            self.check_experience_to_level_up()
