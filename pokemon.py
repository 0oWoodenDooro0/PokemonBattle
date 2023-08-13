import io
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
        self.level: int = 1
        self.name: str | None = None
        self.health_bar: HealthBar | None = None
        self.set_sprite()
        self.set_pokemon_data()

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

    def set_pokemon_data(self):
        self.name = self.data["name"]
        if self.front:
            self.health_bar = HealthBar(c.POKEMON_IMAGE_SIZE // 2, c.POKEMON_IMAGE_SIZE // 4, 200, 20, 100)
        else:
            self.health_bar = HealthBar(c.SCREEN_WIDTH - c.POKEMON_IMAGE_SIZE // 2, c.SCREEN_HEIGHT - c.PANEL_HEIGHT - c.POKEMON_IMAGE_SIZE // 4, 200, 20, 100)

    def draw(self, screen: pg.Surface):
        self.health_bar.draw(screen)
        screen.blit(self.sprite, self.sprite_rect)
