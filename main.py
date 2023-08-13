import pygame as pg
from urllib.request import urlopen
import io
from health_bar import HealthBar

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PANEL_HEIGHT = 200
POKEMON_SIZE = 300
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
pg.draw.line(panel, BLACK, (SCREEN_WIDTH * 0.6, 0), (SCREEN_WIDTH * 0.6, PANEL_HEIGHT), 2)
panel_rect = panel.get_rect()
panel_rect.topleft = (0, SCREEN_HEIGHT - PANEL_HEIGHT)
front_image_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/4.png"
back_image_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/1.png"
front_image_stream = urlopen(front_image_url).read()
back_image_stream = urlopen(back_image_url).read()
front_image_file = io.BytesIO(front_image_stream)
back_image_file = io.BytesIO(back_image_stream)
front_image = pg.image.load(front_image_file).convert_alpha()
back_image = pg.image.load(back_image_file).convert_alpha()
front_image = pg.transform.scale(front_image, (POKEMON_SIZE, POKEMON_SIZE))
back_image = pg.transform.scale(back_image, (POKEMON_SIZE, POKEMON_SIZE))
front_image_rect = front_image.get_rect()
back_image_rect = back_image.get_rect()
front_image_rect.topright = (SCREEN_WIDTH, 0)
back_image_rect.bottomleft = (0, SCREEN_HEIGHT - PANEL_HEIGHT)
front_health_bar = HealthBar(POKEMON_SIZE // 2, POKEMON_SIZE // 4, 200, 20, 100)
back_health_bar = HealthBar(SCREEN_WIDTH - POKEMON_SIZE // 2, SCREEN_HEIGHT - PANEL_HEIGHT - POKEMON_SIZE // 4, 200, 20, 100)

run = True
while run:
    clock.tick(FPS)

    screen.fill(WHITE)
    screen.blit(back_image, back_image_rect)
    screen.blit(front_image, front_image_rect)
    screen.blit(panel, panel_rect)
    front_health_bar.draw(screen)
    back_health_bar.draw(screen)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            run = False

    pg.display.flip()
