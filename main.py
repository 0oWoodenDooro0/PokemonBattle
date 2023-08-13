import json

import pygame as pg

import constants as c
import util
from button import Button
from pokemon import Pokemon

TITLE = "Pokemon Battle"
FPS = 60

pg.init()

clock = pg.time.Clock()

screen = pg.display.set_mode((c.SCREEN_WIDTH, c.SCREEN_HEIGHT))
pg.display.set_caption(TITLE)

TEXT_FONT = pg.font.Font('assets/ARCADECLASSIC.TTF', 28)

panel = pg.Surface((c.SCREEN_WIDTH, c.PANEL_HEIGHT))
panel.fill(c.WHITE)
pg.draw.line(panel, c.BLACK, (0, 0), (c.SCREEN_WIDTH, 0), 2)
pg.draw.line(panel, c.BLACK, (0, 0), (c.SCREEN_WIDTH, 0), 2)
pg.draw.line(panel, c.BLACK, (c.PANEL_WIDTH, 0), (c.PANEL_WIDTH, c.PANEL_HEIGHT), 2)
pg.draw.line(panel, c.BLACK, (c.PANEL_WIDTH + 20, c.PANEL_HEIGHT // 2), (c.SCREEN_WIDTH - 20, c.PANEL_HEIGHT // 2), 1)
pg.draw.line(panel, c.BLACK, ((c.SCREEN_WIDTH + c.PANEL_WIDTH) // 2, 20), ((c.SCREEN_WIDTH + c.PANEL_WIDTH) // 2, c.PANEL_HEIGHT - 20), 1)
panel_rect = panel.get_rect()
panel_rect.topleft = (0, c.SCREEN_HEIGHT - c.PANEL_HEIGHT)
front_value_image = pg.image.load('assets/image/front_value.png').convert_alpha()
back_value_image = pg.image.load('assets/image/back_value.png').convert_alpha()
front_value_image_rect = front_value_image.get_rect()
back_value_image_rect = back_value_image.get_rect()
front_value_image_rect.center = c.FRONT_VALUE_POS
back_value_image_rect.center = c.BACK_VALUE_POS

with open('pokemon1.json') as f:
    d = json.load(f)
    front_pokemon = Pokemon(d, front=True)

with open('pokemon2.json') as f:
    d = json.load(f)
    back_pokemon = Pokemon(d)

fight_button_image = pg.image.load('assets/button/fight_button.png').convert_alpha()
bag_button_image = pg.image.load('assets/button/bag_button.png').convert_alpha()
pokemon_button_image = pg.image.load('assets/button/pokemon_button.png').convert_alpha()
run_button_image = pg.image.load('assets/button/run_button.png').convert_alpha()

fight_button = Button(c.PANEL_WIDTH + (c.SCREEN_WIDTH - c.PANEL_WIDTH) // 4, c.SCREEN_HEIGHT - c.PANEL_HEIGHT * 3 // 4, fight_button_image, center=True)
bag_button = Button(c.PANEL_WIDTH + (c.SCREEN_WIDTH - c.PANEL_WIDTH) * 3 // 4, c.SCREEN_HEIGHT - c.PANEL_HEIGHT * 3 // 4, bag_button_image, center=True)
pokemon_button = Button(c.PANEL_WIDTH + (c.SCREEN_WIDTH - c.PANEL_WIDTH) // 4, c.SCREEN_HEIGHT - c.PANEL_HEIGHT // 4, pokemon_button_image, center=True)
run_button = Button(c.PANEL_WIDTH + (c.SCREEN_WIDTH - c.PANEL_WIDTH) * 3 // 4, c.SCREEN_HEIGHT - c.PANEL_HEIGHT // 4, run_button_image, center=True)

run = True
while run:
    clock.tick(FPS)

    screen.fill(c.WHITE)
    screen.blit(panel, panel_rect)
    screen.blit(back_value_image, back_value_image_rect)
    screen.blit(front_value_image, front_value_image_rect)
    front_pokemon.draw(screen)
    back_pokemon.draw(screen)

    util.draw_text(front_pokemon.name, TEXT_FONT, c.BLACK, (c.FRONT_VALUE_POS[0] - 90, c.FRONT_VALUE_POS[1] - 40), screen, True)
    util.draw_text(f'Lv {front_pokemon.level}', TEXT_FONT, c.BLACK, (c.FRONT_VALUE_POS[0] + 60, c.FRONT_VALUE_POS[1] - 40), screen, True)
    util.draw_text(back_pokemon.name, TEXT_FONT, c.BLACK, (c.BACK_VALUE_POS[0] - 90 + 64, c.BACK_VALUE_POS[1] - 40), screen, True)
    util.draw_text(f'Lv {back_pokemon.level}', TEXT_FONT, c.BLACK, (c.BACK_VALUE_POS[0] + 60 + 64, c.BACK_VALUE_POS[1] - 40), screen, True)

    if fight_button.draw(screen):
        pass
    if bag_button.draw(screen):
        pass
    if pokemon_button.draw(screen):
        pass
    if run_button.draw(screen):
        pass

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            run = False

    pg.display.flip()
