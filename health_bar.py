import pygame as pg


class HealthBar:
    def __init__(self, x: int, y: int, w: int, h: int, max_hp: int):
        self.x: int = x
        self.y: int = y
        self.w: int = w
        self.h: int = h
        self.hp: int = max_hp
        self.temp_hp: float = self.hp
        self.max_hp: int = max_hp

    def draw(self, surface: pg.Surface) -> None:
        ratio: float = self.temp_hp / self.max_hp
        color: str = "green" if ratio > 0.5 else "yellow" if ratio > 0.3 else "red"
        pg.draw.rect(surface, color, (self.x - self.w // 2, self.y - self.h // 2, self.w * ratio, self.h))

    def update(self, hp: int) -> None:
        self.hp = hp
        if abs(self.temp_hp - self.hp) < self.max_hp * 0.005:
            self.temp_hp = self.hp
        elif self.temp_hp > self.hp:
            self.temp_hp -= self.max_hp * 0.005
        elif self.temp_hp < self.hp:
            self.temp_hp += self.max_hp * 0.005
