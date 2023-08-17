import math

import pygame as pg
import json

from pokemon import Pokemon


def draw_text(text: str, font: pg.font.Font, text_color: pg.Color, pos: tuple[int, int], surface: pg.Surface, center: bool = False, mid_left: bool = False):
    img = font.render(text, True, text_color)
    if center:
        img_rect = img.get_rect(center=pos)
        surface.blit(img, img_rect)
    elif mid_left:
        img_rect = img.get_rect(midleft=pos)
        surface.blit(img, img_rect)
    else:
        surface.blit(img, pos)


def fetch_json(directory: str, file_name: str):
    with open(f'{directory}/{file_name}.json') as f:
        data = json.load(f)
        return data


def url_to_id(url: str, prefix: str):
    return int(url.removeprefix(prefix).removesuffix('/'))


def type_in_pokemon(data: list, pokemon_type: int):
    for d in data:
        if int(url_to_id(d['url'], 'https://pokeapi.co/api/v2/type/')) == pokemon_type:
            return True
    return False


def get_battle_experience(defender_pokemon: Pokemon):
    return math.floor(defender_pokemon.base_experience * defender_pokemon.level / 7)
