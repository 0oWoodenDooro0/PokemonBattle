import io
from urllib.request import urlopen

import pygame as pg

from button import Button
from health_bar import HealthBar

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PANEL_HEIGHT = 200
PANEL_WIDTH = 450
POKEMON_SIZE = 300
FRONT_VALUE_POS: tuple[int, int] = (POKEMON_SIZE // 2 + 34, POKEMON_SIZE // 4 - 10)
BACK_VALUE_POS: tuple[int, int] = (SCREEN_WIDTH - POKEMON_SIZE // 2 - 68, SCREEN_HEIGHT - PANEL_HEIGHT - POKEMON_SIZE // 4 - 10)
TITLE = "Pokemon Battle"
FPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

pg.init()

clock = pg.time.Clock()

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption(TITLE)

panel = pg.Surface((SCREEN_WIDTH, PANEL_HEIGHT))
panel.fill(WHITE)
pg.draw.line(panel, BLACK, (0, 0), (SCREEN_WIDTH, 0), 2)
pg.draw.line(panel, BLACK, (0, 0), (SCREEN_WIDTH, 0), 2)
pg.draw.line(panel, BLACK, (PANEL_WIDTH, 0), (PANEL_WIDTH, PANEL_HEIGHT), 2)
pg.draw.line(panel, BLACK, (PANEL_WIDTH + 20, PANEL_HEIGHT // 2), (SCREEN_WIDTH - 20, PANEL_HEIGHT // 2), 1)
pg.draw.line(panel, BLACK, ((SCREEN_WIDTH + PANEL_WIDTH) // 2, 20), ((SCREEN_WIDTH + PANEL_WIDTH) // 2, PANEL_HEIGHT - 20), 1)
panel_rect = panel.get_rect()
panel_rect.topleft = (0, SCREEN_HEIGHT - PANEL_HEIGHT)
front_value_image = pg.image.load('assets/image/front_value.png').convert_alpha()
back_value_image = pg.image.load('assets/image/back_value.png').convert_alpha()
front_value_image_rect = front_value_image.get_rect()
back_value_image_rect = back_value_image.get_rect()
front_value_image_rect.center = FRONT_VALUE_POS
back_value_image_rect.center = BACK_VALUE_POS
front_image_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png"
back_image_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/1.png"
front_image_stream = urlopen(front_image_url).read()
back_image_stream = urlopen(back_image_url).read()
front_image_file = io.BytesIO(front_image_stream)
back_image_file = io.BytesIO(back_image_stream)
front_image = pg.image.load(front_image_file).convert()
back_image = pg.image.load(back_image_file).convert()
front_image = pg.transform.scale(front_image, (POKEMON_SIZE, POKEMON_SIZE))
back_image = pg.transform.scale(back_image, (POKEMON_SIZE, POKEMON_SIZE))
front_image_rect = front_image.get_rect()
back_image_rect = back_image.get_rect()
front_image_rect.topright = (SCREEN_WIDTH, - POKEMON_SIZE // 4)
back_image_rect.bottomleft = (0, SCREEN_HEIGHT - PANEL_HEIGHT + POKEMON_SIZE // 4)
front_health_bar = HealthBar(POKEMON_SIZE // 2, POKEMON_SIZE // 4, 200, 20, 100)
back_health_bar = HealthBar(SCREEN_WIDTH - POKEMON_SIZE // 2, SCREEN_HEIGHT - PANEL_HEIGHT - POKEMON_SIZE // 4, 200, 20, 100)

fight_button_image = pg.image.load('assets/button/fight_button.png').convert_alpha()
bag_button_image = pg.image.load('assets/button/bag_button.png').convert_alpha()
pokemon_button_image = pg.image.load('assets/button/pokemon_button.png').convert_alpha()
run_button_image = pg.image.load('assets/button/run_button.png').convert_alpha()

text_font = pg.font.Font('assets/ARCADECLASSIC.TTF', 28)

fight_button = Button(PANEL_WIDTH + (SCREEN_WIDTH - PANEL_WIDTH) // 4, SCREEN_HEIGHT - PANEL_HEIGHT * 3 // 4, fight_button_image, center=True)
bag_button = Button(PANEL_WIDTH + (SCREEN_WIDTH - PANEL_WIDTH) * 3 // 4, SCREEN_HEIGHT - PANEL_HEIGHT * 3 // 4, bag_button_image, center=True)
pokemon_button = Button(PANEL_WIDTH + (SCREEN_WIDTH - PANEL_WIDTH) // 4, SCREEN_HEIGHT - PANEL_HEIGHT // 4, pokemon_button_image, center=True)
run_button = Button(PANEL_WIDTH + (SCREEN_WIDTH - PANEL_WIDTH) * 3 // 4, SCREEN_HEIGHT - PANEL_HEIGHT // 4, run_button_image, center=True)


def draw_text(text: str, font, text_color, pos, center=False):
    img = font.render(text, True, text_color)
    if center:
        img_rect = img.get_rect(center=pos)
        screen.blit(img, img_rect)
    else:
        screen.blit(img, pos)


run = True
while run:
    clock.tick(FPS)

    screen.fill(WHITE)
    screen.blit(back_image, back_image_rect)
    screen.blit(front_image, front_image_rect)
    screen.blit(panel, panel_rect)
    screen.blit(back_value_image, back_value_image_rect)
    screen.blit(front_value_image, front_value_image_rect)
    front_health_bar.draw(screen)
    back_health_bar.draw(screen)

    draw_text("charmander", text_font, BLACK, (FRONT_VALUE_POS[0] - 90, FRONT_VALUE_POS[1] - 40), True)
    draw_text(f'Lv 100', text_font, BLACK, (FRONT_VALUE_POS[0] + 60, FRONT_VALUE_POS[1] - 40), True)
    draw_text("bulbasaur", text_font, BLACK, (BACK_VALUE_POS[0] - 90 + 64, BACK_VALUE_POS[1] - 40), True)
    draw_text(f'Lv 100', text_font, BLACK, (BACK_VALUE_POS[0] + 60 + 64, BACK_VALUE_POS[1] - 40), True)

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
