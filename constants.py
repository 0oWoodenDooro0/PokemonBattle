from pygame import Color

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
PANEL_HEIGHT: int = 200
PANEL_WIDTH: int = 450
POKEMON_IMAGE_SIZE: int = 300
FRONT_VALUE_POS: tuple[int, int] = (POKEMON_IMAGE_SIZE // 2 + 34, POKEMON_IMAGE_SIZE // 4 - 10)
BACK_VALUE_POS: tuple[int, int] = (SCREEN_WIDTH - POKEMON_IMAGE_SIZE // 2 - 68, SCREEN_HEIGHT - PANEL_HEIGHT - POKEMON_IMAGE_SIZE // 4 - 10)
BLACK: Color = Color(0, 0, 0)
WHITE: Color = Color(255, 255, 255)
GREY: Color = Color(240, 240, 240)
MESSAGE_POS_LINE_1: tuple[int, int] = (20, 60)
MESSAGE_POS_LINE_2: tuple[int, int] = (20, 140)
MOVE_CATEGORY: list[int] = [0, 1, 2, 3, 4, 6, 8, 9, 10, 11, 12, 13]
