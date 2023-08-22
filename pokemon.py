import io
import math
import random
from typing import Any
from urllib.request import urlopen

import pygame as pg

import constants as const
import util
from generation import Generation
from health_bar import HealthBar
from move import Move
from move_result import MoveResult


class Pokemon:
    def __init__(self, pokemon_id: int, generation: Generation, enemy: bool = False):
        self.generation: Generation = generation
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

    def set_pokemon_data(self) -> None:
        self.basic_stats = {}
        self.basic_points = {}
        self.stats_effect = {}
        for stat in self.data['stats']:
            stat_id: int = util.url_to_id(stat['stat']['url'], 'stat')
            self.basic_stats[stat_id] = stat['base_stat']
            self.basic_points[stat_id] = 0
            self.stats_effect[stat_id] = 0
        self.stats_effect[7] = 0
        self.stats_effect[8] = 0

    def get_basic_stats(self) -> dict:
        return {util.url_to_id(stat['stat']['url'], 'stat'): stat['base_stat'] for stat in self.data['stats']}

    @staticmethod
    def get_basic_point() -> dict:
        return {i + 1: 0 for i in range(6)}

    @staticmethod
    def reset_stats_effect() -> dict:
        return {i + 1: 0 for i in range(8)}

    def get_moves(self) -> list:
        move_list: list = self.data['moves']
        moves: list = []
        for m in move_list:
            move_id: int = util.url_to_id(m['move']['url'], 'move')
            if move_id in self.generation.moves and len(moves) < 4:
                move: Move = Move(move_id)
                if move.category in [0, 2, 3, 6, 8, 9]:
                    moves.append(move)
        return moves

    def get_health_bar(self) -> HealthBar:
        if self.enemy:
            return HealthBar(const.POKEMON_IMAGE_SIZE // 2, const.POKEMON_IMAGE_SIZE // 4, 200, 20, self.stats[1])
        else:
            return HealthBar(const.SCREEN_WIDTH - const.POKEMON_IMAGE_SIZE // 2, const.SCREEN_HEIGHT - const.PANEL_HEIGHT - const.POKEMON_IMAGE_SIZE // 4, 200, 20,
                             self.stats[1])

    def get_levels(self) -> list:
        species_data: dict = util.fetch_json('pokemon-species', str(self.species))
        growth_rate_id: int = util.url_to_id(species_data['growth_rate']['url'], 'growth-rate')
        growth_rate_data: dict = util.fetch_json('growth-rate', str(growth_rate_id))
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

    def get_stat_effect(self, stat_id: int) -> float:
        level = self.stats_effect[stat_id]
        if level > 0:
            return math.floor((level + 2) / 2 * 100) / 100
        elif level < 0:
            return math.floor(2 / (abs(level) + 2) * 100) / 100
        else:
            return 1

    def get_sprite(self) -> tuple[pg.Surface, pg.Rect]:
        image_url: str = self.data['sprites']['front_default'] if self.enemy else self.data['sprites']['back_default']
        image_stream: Any = urlopen(image_url).read()
        image_file: io.BytesIO = io.BytesIO(image_stream)
        sprite: pg.Surface = pg.image.load(image_file).convert_alpha()
        sprite: pg.Surface = pg.transform.scale(sprite, (300, 300))
        sprite_rect: pg.Rect = sprite.get_rect()
        if self.enemy:
            sprite_rect.topright = (0, - const.POKEMON_IMAGE_SIZE // 5)
            return sprite, sprite_rect
        else:
            sprite_rect.bottomleft = (const.SCREEN_WIDTH, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + const.POKEMON_IMAGE_SIZE // 5)
            return sprite, sprite_rect

    def draw(self, screen: pg.Surface) -> None:
        screen.blit(self.sprite, self.sprite_rect)

    def draw_health_bar(self, screen) -> None:
        if self.hp < 0:
            self.hp = 0
        self.health_bar.update(self.hp)
        self.health_bar.draw(screen)

    def add_experience(self, experience: int) -> None:
        self.experience += experience
        self.check_experience_to_level_up()

    def check_experience_to_level_up(self) -> None:
        if self.level == 100:
            return
        if self.experience >= self.levels[self.level + 1]['experience']:
            self.level += 1
            self.check_experience_to_level_up()
