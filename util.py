import math
import os.path

import pygame as pg
import json

import requests as requests

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
    path = os.path.join(directory, f'{file_name}.json')
    if not os.path.isfile(path):
        url = f'https://pokeapi.co/api/v2/{directory}/{file_name}'
        if not os.path.isdir(directory):
            os.makedirs(directory)
        json_data = requests.get(url).json()
        with open(path, 'w') as file:
            json.dump(json_data, file)
    with open(path) as f:
        data = json.load(f)
        return data


def url_to_id(url: str, prefix: str):
    return int(url.removeprefix(f'https://pokeapi.co/api/v2/{prefix}/').removesuffix('/'))


def type_in_pokemon(data: list, pokemon_type: int):
    for d in data:
        if int(url_to_id(d['url'], 'type')) == pokemon_type:
            return True
    return False


def get_battle_experience(defender_pokemon: Pokemon):
    return math.floor(defender_pokemon.base_experience * defender_pokemon.level / 7)
