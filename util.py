import pygame as pg


def draw_text(text: str, font, text_color, pos, surface: pg.Surface, center=False):
    img = font.render(text, True, text_color)
    if center:
        img_rect = img.get_rect(center=pos)
        surface.blit(img, img_rect)
    else:
        surface.blit(img, pos)
