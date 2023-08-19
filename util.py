import json
import math
import os.path
from typing import Any

import pygame as pg
import requests as requests

from pokemon import Pokemon


def draw_text(text: str, font: pg.font.Font, text_color: pg.Color, pos: tuple[int, int], surface: pg.Surface, center: bool = False, mid_left: bool = False) -> None:
    img: pg.Surface = font.render(text, True, text_color)
    if center:
        img_rect: pg.Rect = img.get_rect(center=pos)
        surface.blit(img, img_rect)
    elif mid_left:
        img_rect: pg.Rect = img.get_rect(midleft=pos)
        surface.blit(img, img_rect)
    else:
        surface.blit(img, pos)


def fetch_json(directory: str, file_name: str) -> dict:
    path: str = os.path.join(directory, f'{file_name}.json')
    if not os.path.isfile(path):
        url: str = f'https://pokeapi.co/api/v2/{directory}/{file_name}'
        if not os.path.isdir(directory):
            os.makedirs(directory)
        json_data: Any = requests.get(url).json()
        with open(path, 'w') as file:
            json.dump(json_data, file)
    with open(path) as f:
        data: dict = json.load(f)
        return data


def fetch_all_stat() -> None:
    for i in range(8):
        path: str = os.path.join('stat', f'{i + 1}.json')
        if not os.path.isfile(path):
            url: str = f'https://pokeapi.co/api/v2/stat/{i + 1}'
            if not os.path.isdir('stat'):
                os.makedirs('stat')
            json_data: Any = requests.get(url).json()
            with open(path, 'w') as file:
                json.dump(json_data, file)


def url_to_id(url: str, prefix: str) -> int:
    return int(url.removeprefix(f'https://pokeapi.co/api/v2/{prefix}/').removesuffix('/'))


def type_in_pokemon(data: list, pokemon_type: int) -> bool:
    for d in data:
        if int(url_to_id(d['url'], 'type')) == pokemon_type:
            return True
    return False


def get_battle_experience(defender_pokemon: Pokemon) -> int:
    return math.floor(defender_pokemon.base_experience * defender_pokemon.level / 7)
