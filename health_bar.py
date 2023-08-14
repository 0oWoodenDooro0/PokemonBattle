import pygame as pg


class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp

    def draw(self, surface):
        ratio = self.hp / self.max_hp
        color = "green" if ratio > 0.7 else "yellow" if ratio > 0.3 else "red"
        pg.draw.rect(surface, color, (self.x - self.w // 2, self.y - self.h // 2, self.w * ratio, self.h))

    def update(self, hp):
        self.hp = hp
