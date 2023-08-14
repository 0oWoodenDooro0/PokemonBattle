import pygame as pg
import json


def draw_text(text: str, font, text_color, pos, surface: pg.Surface, center=False):
    img = font.render(text, True, text_color)
    if center:
        img_rect = img.get_rect(center=pos)
        surface.blit(img, img_rect)
    else:
        surface.blit(img, pos)


def fetch_json(file: str):
    with open(file) as f:
        data = json.load(f)
        return data


def url_to_id(url: str, prefix: str):
    return int(url.removeprefix(prefix).removesuffix('/'))


def type_in_pokemon(data: list, pokemon_type: int):
    for t in data:
        if int(url_to_id(t['url'], 'https://pokeapi.co/api/v2/type/')) == pokemon_type:
            return True
    return False
