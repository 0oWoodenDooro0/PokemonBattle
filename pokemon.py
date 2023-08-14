import io
import math
import random
from urllib.request import urlopen

import pygame as pg

import constants as c
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
        self.effort_values: dict | None = None
        self.individual_level: dict | None = None
        self.stats: dict | None = None
        self.hp: int | None = None
        self.types: list | None = None
        self.level: int = 1
        self.health_bar: HealthBar | None = None
        self.set_sprite()
        self.set_pokemon_data()

    def set_pokemon_data(self):
        self.pokemon_id = self.data["id"]
        self.name = self.data["name"]

        self.types = [x['type']['name'] for x in self.data['types']]

        self.basic_stats = {}
        for stat in self.data['stats']:
            stat_name = stat['stat']['name']
            self.basic_stats[stat_name] = stat['base_stat']

        self.effort_values = {}
        for stat in self.data['stats']:
            stat_name = stat['stat']['name']
            self.effort_values[stat_name] = stat['effort']

        self.individual_level = self.get_individual_level()

        self.stats = self.get_stat()

        self.hp = self.stats["hp"]

        if self.front:
            self.health_bar = HealthBar(c.POKEMON_IMAGE_SIZE // 2, c.POKEMON_IMAGE_SIZE // 4, 200, 20, self.stats["hp"])
        else:
            self.health_bar = HealthBar(c.SCREEN_WIDTH - c.POKEMON_IMAGE_SIZE // 2, c.SCREEN_HEIGHT - c.PANEL_HEIGHT - c.POKEMON_IMAGE_SIZE // 4, 200, 20, self.stats["hp"])

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
        return math.floor((self.basic_stats['hp'] * 2 + self.individual_level['hp'] + self.effort_values['hp'] / 4) * (
                self.level / 100) + self.level + 10)

    def get_other_ability(self, stat: str, character: int = 1) -> int:
        return math.floor(((self.basic_stats[stat] * 2 + self.individual_level[stat] + self.effort_values[stat] / 4) * (
                self.level / 100) + 5) * character)

    def set_sprite(self):
        image_url = self.data["sprites"]["front_default"] if self.front else self.data["sprites"]["back_default"]
        image_stream = urlopen(image_url).read()
        image_file = io.BytesIO(image_stream)
        self.sprite = pg.image.load(image_file).convert_alpha()
        self.sprite = pg.transform.scale(self.sprite, (300, 300))
        self.sprite_rect = self.sprite.get_rect()
        if self.front:
            self.sprite_rect.topright = (c.SCREEN_WIDTH, - c.POKEMON_IMAGE_SIZE // 4)
        else:
            self.sprite_rect.bottomleft = (0, c.SCREEN_HEIGHT - c.PANEL_HEIGHT + c.POKEMON_IMAGE_SIZE // 4)

    def draw(self, screen: pg.Surface):
        self.health_bar.draw(screen)
        screen.blit(self.sprite, self.sprite_rect)
        self.health_bar.update(self.hp)
