import os.path

import pygame as pg

import constants as const
import util
from battle import Battle
from generation import Generation
from pokemon import Pokemon
from state import BattleState, AttackState

TITLE = "Pokemon Battle"
FPS = 60

pg.mixer.pre_init()
pg.mixer.init()
pg.init()

clock: pg.time.Clock = pg.time.Clock()

screen: pg.Surface = pg.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
pg.display.set_caption(TITLE)

generation: Generation = Generation(1)

front_pokemon: Pokemon = Pokemon(7, generation, enemy=True)
back_pokemon: Pokemon = Pokemon(15, generation)
battle: Battle = Battle(front_pokemon, back_pokemon)

pg.mixer.music.load(os.path.join('soundtrack', 'Battle Music.mp3'))
pg.mixer.music.set_volume(0.05)
pg.mixer.music.play(loops=-1)

while battle.run:
    clock.tick(FPS)

    screen.fill(const.GREY)

    battle.update(screen)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            battle.run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            battle.run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            battle.mouse_click()

    pg.display.flip()
