import math
import os
import random
from typing import Optional

import pygame as pg

import constants as const
import util
from button import Button
from move import Move
from move_result import MoveResult
from pokemon import Pokemon
from state import BattleState, AttackState


class Battle:
    def __init__(
            self, front_pokemon: Pokemon, back_pokemon: Pokemon,
    ):
        self.text_font: pg.font.Font = pg.font.Font(os.path.join('assets', 'pokemon_pixel_font.ttf'), 40)
        self.message_font: pg.font.Font = pg.font.Font(os.path.join('assets', 'pokemon_pixel_font.ttf'), 60)

        front_value_image: pg.Surface = pg.image.load(os.path.join('assets', 'image', 'front_value.png')).convert_alpha()
        front_value_image_rect: pg.Rect = front_value_image.get_rect()
        front_value_image_rect.center = const.FRONT_VALUE_POS
        back_value_image: pg.Surface = pg.image.load(os.path.join('assets', 'image', 'back_value.png')).convert_alpha()
        back_value_image_rect: pg.Rect = back_value_image.get_rect()
        back_value_image_rect.center = const.BACK_VALUE_POS

        self.attribute_panel: pg.Surface = pg.Surface((const.SCREEN_WIDTH - const.PANEL_WIDTH, const.PANEL_HEIGHT))
        self.attribute_panel_rect: pg.Rect = self.attribute_panel.get_rect()
        self.attribute_panel_rect.topleft = (const.PANEL_WIDTH, const.SCREEN_HEIGHT - const.PANEL_HEIGHT)

        self.move_panel: pg.Surface = pg.Surface((const.PANEL_WIDTH, const.PANEL_HEIGHT))
        self.move_panel_rect: pg.Rect = self.move_panel.get_rect()
        self.move_panel_rect.topleft = (0, const.SCREEN_HEIGHT - const.PANEL_HEIGHT)

        self.selection_image: pg.Surface = pg.image.load(os.path.join('assets', 'button', 'selection_button.png')).convert_alpha()
        self.move_button_image: pg.Surface = pg.image.load(os.path.join('assets', 'button', 'move_button.png')).convert_alpha()

        self.selection_buttons: list[Button] = []
        self.selection_button_texts: list[str] = ['FIGHT', 'BAG', 'POKEMON', 'RUN']
        for i in range(4):
            x: int = const.PANEL_WIDTH + (const.SCREEN_WIDTH - const.PANEL_WIDTH) // 4 * (1 if i % 2 == 0 else 3)
            y: int = const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4 * (3 if i // 2 == 0 else 1)
            selection_button: Button = Button((x, y), self.selection_image, center=True)
            self.selection_buttons.append(selection_button)

        self.move_buttons: list[Button] = []
        for i in range(4):
            x: int = const.PANEL_WIDTH // 4 * (1 if i % 2 == 0 else 3)
            y: int = const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4 * (3 if i // 2 == 0 else 1)
            move_button: Button = Button((x, y), self.move_button_image, check_mouse_on=True, center=True)
            self.move_buttons.append(move_button)
        self.front_pokemon = front_pokemon
        self.back_pokemon = back_pokemon
        self.front_data: dict = {
            'pokemon': front_pokemon,
            'value_image': front_value_image,
            'value_image_rect': front_value_image_rect
        }
        self.back_data: dict = {
            'pokemon': back_pokemon,
            'value_image': back_value_image,
            'value_image_rect': back_value_image_rect
        }

        self.battle_state: BattleState = BattleState.PREBATTLE
        self.attack_state: AttackState = AttackState.FIRST_ATTACK

        self.back_move: Optional[Move] = None
        self.front_move: Optional[Move] = None
        self.first_move: Optional[Move] = None
        self.first_pokemon: Optional[Pokemon] = None
        self.last_move: Optional[Move] = None
        self.last_pokemon: Optional[Pokemon] = None
        self.attack_result: Optional[MoveResult] = None
        self.stat_change_num: int = 0
        self.damage_time: list[int, int] = [0, 0]

        self.button_select_sound: pg.mixer.Sound = pg.mixer.Sound(os.path.join('sound_effect', 'Button Select.wav'))
        self.hurt_sound: pg.mixer.Sound = pg.mixer.Sound(os.path.join('sound_effect', 'Hurt.wav'))

        util.fetch_all_stat()

    def update(self, screen: pg.Surface, run: bool):

        self.move_panel.fill(const.WHITE)
        self.attribute_panel.fill(const.WHITE)

        if self.battle_state is not BattleState.PREBATTLE:
            screen.blit(self.front_data.get('value_image'), self.front_data.get('value_image_rect'))
            screen.blit(self.back_data.get('value_image'), self.back_data.get('value_image_rect'))
            front_pokemon: Pokemon = self.front_data.get('pokemon')
            back_pokemon: Pokemon = self.back_data.get('pokemon')
            front_pokemon.draw_health_bar(screen)
            back_pokemon.draw_health_bar(screen)

            util.draw_text(front_pokemon.name, self.text_font, const.BLACK, (const.FRONT_VALUE_POS[0] - 150, const.FRONT_VALUE_POS[1] - 50), screen)
            util.draw_text(f'Lv{front_pokemon.level}', self.text_font, const.BLACK, (const.FRONT_VALUE_POS[0] + 40, const.FRONT_VALUE_POS[1] - 50), screen)
            util.draw_text(back_pokemon.name, self.text_font, const.BLACK, (const.BACK_VALUE_POS[0] - 150 + 64, const.BACK_VALUE_POS[1] - 50), screen)
            util.draw_text(f'Lv{back_pokemon.level}', self.text_font, const.BLACK, (const.BACK_VALUE_POS[0] + 40 + 64, const.BACK_VALUE_POS[1] - 50), screen)
            util.draw_text(f'{back_pokemon.hp}/{back_pokemon.stats[1]}', self.text_font, const.BLACK, (const.BACK_VALUE_POS[0] + 70, const.BACK_VALUE_POS[1] + 40), screen, True)

        if self.battle_state is BattleState.SELECTION or self.battle_state is BattleState.FIGHT:
            pg.draw.line(screen, const.BLACK, (const.PANEL_WIDTH, const.SCREEN_HEIGHT - const.PANEL_HEIGHT), (const.PANEL_WIDTH, const.SCREEN_HEIGHT), 2)

            for i in range(4):
                x: int = (const.SCREEN_WIDTH - const.PANEL_WIDTH) // 4 * (1 if i % 2 == 0 else 3)
                y: int = const.PANEL_HEIGHT // 4 * (1 if i // 2 == 0 else 3)
                util.draw_text(self.selection_button_texts[i], self.text_font, const.BLACK, (x, y), self.attribute_panel, center=True)
                if self.selection_buttons[i].draw(screen) and self.battle_state != BattleState.ATTACK:
                    self.button_select_sound.play()
                    match i:
                        case 0:
                            self.battle_state = BattleState.FIGHT
                        case 1:
                            pass
                        case 2:
                            pass
                        case 3:
                            run = False
            pg.draw.line(self.attribute_panel, const.BLACK, (0, 0), (0, const.PANEL_HEIGHT), 2)

        if self.damage_time[0] % 20 < 10 or self.damage_time[0] > 60:
            self.front_pokemon.draw(screen)
        if self.damage_time[1] % 20 < 10 or self.damage_time[1] > 60:
            self.back_pokemon.draw(screen)

        match self.battle_state:

            case BattleState.PREBATTLE:
                if self.front_pokemon.sprite_rect.right != const.SCREEN_WIDTH and self.back_pokemon.sprite_rect.left != 0:
                    self.front_pokemon.sprite_rect.right += 5
                    self.back_pokemon.sprite_rect.left -= 5
                else:
                    self.battle_state = BattleState.SELECTION

            case BattleState.SELECTION:
                util.draw_text('What will', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                util.draw_text(f'{self.back_pokemon.name} do?', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

            case BattleState.FIGHT:
                for i in range(len(self.back_pokemon.moves)):
                    x: int = const.PANEL_WIDTH // 4 * (1 if i % 2 == 0 else 3)
                    y: int = const.PANEL_HEIGHT // 4 * (1 if i // 2 == 0 else 3) - 20
                    util.draw_text(f'{self.back_pokemon.moves[i].name}', self.text_font, const.BLACK, (x, y), self.move_panel, True)
                    util.draw_text(f'{self.back_pokemon.moves[i].pp}/{self.back_pokemon.moves[i].max_pp}', self.text_font, const.BLACK, (x, y + 40), self.move_panel, True)
                    button_click: tuple[bool, bool] = self.move_buttons[i].draw(screen)
                    if button_click[0] and self.back_pokemon.moves[i].pp != 0:
                        self.button_select_sound.play()
                        self.back_move = self.back_pokemon.moves[i]
                        self.front_move = random.choice(self.front_pokemon.moves)
                        if self.back_move.priority > self.front_move.priority:
                            self.first_move = self.back_move
                            self.first_pokemon = self.back_pokemon
                            self.last_move = self.front_move
                            self.last_pokemon = self.front_pokemon
                        elif self.back_move.priority < self.front_move.priority:
                            self.first_move = self.back_move
                            self.first_pokemon = self.back_pokemon
                            self.last_move = self.front_move
                        else:
                            if self.back_pokemon.stats[6] >= self.front_pokemon.stats[6]:
                                self.first_move = self.back_move
                                self.first_pokemon = self.back_pokemon
                                self.last_move = self.front_move
                                self.last_pokemon = self.front_pokemon
                            else:
                                self.first_move = self.front_move
                                self.first_pokemon = self.front_pokemon
                                self.last_move = self.back_move
                                self.last_pokemon = self.back_pokemon
                        self.back_move.pp -= 1
                        self.battle_state = BattleState.ATTACK
                        self.attack_state = AttackState.FIRST_ATTACK
                        self.damage_time = [0, 0]
                    elif button_click[1]:
                        self.attribute_panel.fill(const.WHITE)
                        util.draw_text(f'Power: {self.back_pokemon.moves[i].power}', self.text_font, const.BLACK, (20, 20), self.attribute_panel)
                        util.draw_text(f'Accuracy: {self.back_pokemon.moves[i].accuracy}', self.text_font, const.BLACK, (20, 60), self.attribute_panel)
                        type_name: str = util.fetch_json('type', str(self.back_pokemon.moves[i].type))['name'].capitalize()
                        util.draw_text(f'Type: {type_name}', self.text_font, const.BLACK, (20, 100), self.attribute_panel)
                        pg.draw.line(self.attribute_panel, const.BLACK, (0, 0), (0, const.PANEL_HEIGHT), 2)

            case BattleState.DEFEAT:
                self.damage_time = [0, 0]
                if self.front_pokemon.hp == 0:
                    is_enemy: str = 'Enemy ' if self.front_pokemon.enemy else ''
                    util.draw_text(f'{is_enemy}{self.front_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                    util.draw_text(f'fainted!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                elif self.back_pokemon.hp == 0:
                    is_enemy: str = 'Enemy ' if self.back_pokemon.enemy else ''
                    util.draw_text(f'{is_enemy}{self.back_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                    util.draw_text(f'fainted!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

            case BattleState.EXP:
                util.draw_text(f'{self.back_pokemon.name} gained', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                util.draw_text(f'{util.get_battle_experience(self.front_pokemon)} EXP. Points!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

            case BattleState.ATTACK:
                match self.attack_state:
                    case AttackState.FIRST_ATTACK:
                        if self.attack_accuracy(self.first_pokemon, self.first_move, self.last_pokemon):
                            self.attack_result = self.attack(self.first_pokemon, self.first_move, self.last_pokemon)
                            print(self.attack_result)
                            match self.attack_result.move_category:
                                case 2 | 6 | 7:
                                    self.stat_change_num = len(self.attack_result.stat_change_list)
                                case 0 | 6 | 7 | 8 | 9:
                                    self.hurt_sound.play()
                            self.attack_state = AttackState.FIRST_ATTACK_HIT
                        else:
                            self.attack_state = AttackState.FIRST_ATTACK_NOT_HIT

                    case AttackState.FIRST_ATTACK_HIT:
                        if self.attack_result.is_critical:
                            self.damage_time[0 if self.last_pokemon.enemy else 1] += 1
                        is_enemy: str = 'Enemy ' if self.first_pokemon.enemy else ''
                        util.draw_text(f'{is_enemy}{self.first_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                        util.draw_text(f'used {self.first_move.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

                    case AttackState.FIRST_CRICAL_HIT:
                        if self.attack_result.is_critical:
                            self.damage_time[0 if self.last_pokemon.enemy else 1] += 1
                        util.draw_text(f"Critical hit!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)

                    case AttackState.FIRST_EFFECTIVE:
                        if self.attack_result.is_critical:
                            self.damage_time[0 if self.last_pokemon.enemy else 1] += 1
                        is_enemy: str = 'Enemy ' if self.last_pokemon.enemy else ''
                        match self.attack_result.type_effectiveness:
                            case 2 | 4:
                                util.draw_text(f"It's super", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                util.draw_text(f"effective!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                            case 0.5 | 0.25:
                                util.draw_text(f"It's not very", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                util.draw_text(f'effective...', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                            case 0:
                                util.draw_text(f"{is_enemy}{self.last_pokemon.name}", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                            case 1 | None:
                                self.attack_state = AttackState.FIRST_STAT_CHANGE

                        if self.front_pokemon.hp == 0:
                            self.battle_state = BattleState.DEFEAT
                        elif self.back_pokemon.hp == 0:
                            self.battle_state = BattleState.DEFEAT

                    case AttackState.FIRST_STAT_CHANGE:
                        self.damage_time = [0, 0]
                        if self.stat_change_num == 0 or not self.attack_result.stat_change_list:
                            self.attack_state = AttackState.LAST_ATTACK
                        else:
                            target_pokemon: Pokemon = self.attack_result.stat_change_target
                            is_enemy: str = 'Enemy ' if target_pokemon.enemy else ''
                            match self.attack_result.stat_change_list[self.stat_change_num - 1]:
                                case (stat_name, 1):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} rose!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 2):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} rose sharply!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 3):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} rose drastically!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 4):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'maxed its {stat_name}!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 6):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} fell!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 7):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} harshly fell!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 8):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} severely fell!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 9):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f"{stat_name} won't go any higher!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 10):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f"{stat_name} won't go any lower!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

                    case AttackState.FIRST_ATTACK_NOT_HIT:
                        is_enemy: str = 'Enemy ' if self.first_pokemon.enemy else ''
                        util.draw_text(f'{is_enemy}{self.first_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                        util.draw_text(f'attack missed!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

                    case AttackState.LAST_ATTACK:
                        if self.attack_accuracy(self.first_pokemon, self.last_move, self.first_pokemon):
                            self.attack_result = self.attack(self.last_pokemon, self.last_move, self.first_pokemon)
                            print(self.attack_result)
                            match self.attack_result.move_category:
                                case 2 | 6 | 7:
                                    self.stat_change_num = len(self.attack_result.stat_change_list)
                                case 0 | 6 | 7 | 8 | 9:
                                    self.hurt_sound.play()
                            self.attack_state = AttackState.LAST_ATTACK_HIT
                        else:
                            self.attack_state = AttackState.LAST_ATTACK_NOT_HIT

                    case AttackState.LAST_ATTACK_HIT:
                        if self.attack_result.is_critical:
                            self.damage_time[0 if self.first_pokemon.enemy else 1] += 1
                        is_enemy: str = 'Enemy ' if self.last_pokemon.enemy else ''
                        util.draw_text(f'{is_enemy}{self.last_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                        util.draw_text(f'used {self.last_move.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

                    case AttackState.LAST_CRICAL_HIT:
                        if self.attack_result.is_critical:
                            self.damage_time[0 if self.first_pokemon.enemy else 1] += 1
                        util.draw_text(f"Critical Hit!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)

                    case AttackState.LAST_EFFECTIVE:
                        if self.attack_result.is_critical:
                            self.damage_time[0 if self.first_pokemon.enemy else 1] += 1
                        is_enemy: str = 'Enemy ' if self.first_pokemon.enemy else ''
                        match self.attack_result.type_effectiveness:
                            case 2 | 4:
                                util.draw_text(f"It's super", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                util.draw_text(f"effective!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                            case 0.5 | 0.25:
                                util.draw_text(f"It's not very", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                util.draw_text(f"effective...", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                            case 0:
                                util.draw_text(f"It doesn't affect", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                util.draw_text(f"{is_enemy}{self.first_pokemon.name}", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                            case 1 | None:
                                self.attack_state = AttackState.LAST_STAT_CHANGE

                        if self.front_pokemon.hp == 0:
                            self.battle_state = BattleState.DEFEAT
                        elif self.back_pokemon.hp == 0:
                            self.battle_state = BattleState.DEFEAT

                    case AttackState.LAST_STAT_CHANGE:
                        self.damage_time = [0, 0]
                        if self.stat_change_num == 0 or not self.attack_result.stat_change_list:
                            self.battle_state = BattleState.SELECTION
                        else:
                            target_pokemon: Pokemon = self.attack_result.stat_change_target
                            is_enemy = 'Enemy ' if target_pokemon.enemy else ''
                            match self.attack_result.stat_change_list[self.stat_change_num - 1]:
                                case (stat_name, 1):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} rose!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 2):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} rose sharply!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 3):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} rose drastically!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 4):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'maxed its {stat_name}!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 6):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} fell!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 7):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} harshly fell!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 8):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f'{stat_name} severely fell!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 9):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f"{stat_name} won't go any higher!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)
                                case (stat_name, 10):
                                    util.draw_text(f'{is_enemy}{target_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                                    util.draw_text(f"{stat_name} won't go any lower!", self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

                    case AttackState.LAST_ATTACK_NOT_HIT:
                        is_enemy: str = 'Enemy ' if self.last_pokemon.enemy else ''
                        util.draw_text(f'{is_enemy}{self.last_pokemon.name}', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_1, self.move_panel, mid_left=True)
                        util.draw_text(f'attack missed!', self.message_font, const.BLACK, const.MESSAGE_POS_LINE_2, self.move_panel, mid_left=True)

        pg.draw.line(self.move_panel, const.BLACK, (0, 0), (const.PANEL_WIDTH, 0), 2)
        screen.blit(self.move_panel, self.move_panel_rect)
        pg.draw.line(self.attribute_panel, const.BLACK, (0, 0), (const.SCREEN_WIDTH - const.PANEL_WIDTH, 0), 2)
        screen.blit(self.attribute_panel, self.attribute_panel_rect)

    def attack(self, attck_pokemon: 'Pokemon', move: Move, defender_pokemon: 'Pokemon') -> MoveResult:
        print(f'{move.category=}')
        match move.category:
            case 0:
                move_result, damage = self.damage_attack(attck_pokemon, move, defender_pokemon)
                defender_pokemon.hp -= damage
                return move_result
            case 2:
                print(f'{move.stat_chance=}')
                match move.target:
                    case 10 | 11:
                        return self.stat_change(move, defender_pokemon)
                    case 7:
                        return self.stat_change(move, attck_pokemon)
                    case _:
                        raise Exception(f'not define this {move.target=}')
            case 3:
                attck_pokemon.hp += math.floor(move.healing / 100 * attck_pokemon.stats[1])
                if attck_pokemon.hp > attck_pokemon.stats[1]:
                    attck_pokemon.hp = attck_pokemon.stats[1]
                return MoveResult(3)
            case 6:
                move_result, damage = self.damage_attack(attck_pokemon, move, defender_pokemon)
                defender_pokemon.hp -= damage
                if self.stat_accuracy(move.stat_chance):
                    return self.stat_change(move, defender_pokemon, move_result)
                return move_result
            case 7:
                move_result, damage = self.damage_attack(attck_pokemon, move, defender_pokemon)
                defender_pokemon.hp -= damage
                if self.stat_accuracy(move.stat_chance):
                    return self.stat_change(move, attck_pokemon, move_result)
                return move_result
            case 8:
                move_result, damage = self.damage_attack(attck_pokemon, move, defender_pokemon)
                defender_pokemon.hp -= damage
                attck_pokemon.hp += math.floor(move.drain / 100 * damage)
                if attck_pokemon.hp > attck_pokemon.stats[1]:
                    attck_pokemon.hp = attck_pokemon.stats[1]
                return move_result
            case 9:
                defender_pokemon.hp = 0
                return MoveResult(9)
            case _:
                raise Exception(f'not define this {move.category=}')

    @staticmethod
    def damage_attack(attack_pokemon: 'Pokemon', move: Move, defender_pokemon: 'Pokemon', move_result: MoveResult = None) -> tuple[MoveResult, int]:
        if move.crit_rate == 0:
            crit: int = attack_pokemon.basic_stats[6] // 2
        else:
            crit: int = attack_pokemon.basic_stats[6] * 4
        r: int = random.randint(1, 256)
        critical: int = 1 if r > crit else 2
        power: int = move.power
        attack_stat: int = attack_pokemon.stats[2] if move.damage_class == 2 else attack_pokemon.stats[4] if move.damage_class == 3 else 0
        attack: float = attack_stat * attack_pokemon.get_stat_effect(2)
        defense_stat: int = defender_pokemon.stats[3] if move.damage_class == 2 else defender_pokemon.stats[5] if move.damage_class == 3 else 0
        defense: float = defense_stat * attack_pokemon.get_stat_effect(3)
        stab: float = 1.5 if move.type in attack_pokemon.types else 1
        damage: float = (((2 * attack_pokemon.level * critical) / 5 + 2) * power * attack / defense / 50 + 2) * stab
        move_type_data: dict = util.fetch_json('type', str(move.type))['damage_relations']
        type_effectiveness: float = 1
        for i in range(len(defender_pokemon.types)):
            if util.type_in_pokemon(move_type_data['double_damage_to'], defender_pokemon.types[i]):
                damage = damage * 2
                type_effectiveness = type_effectiveness * 2
            elif util.type_in_pokemon(move_type_data['half_damage_to'], defender_pokemon.types[i]):
                damage = damage * 0.5
                type_effectiveness = type_effectiveness * 0.5
            elif util.type_in_pokemon(move_type_data['no_damage_to'], defender_pokemon.types[i]):
                damage = damage * 0
                type_effectiveness = type_effectiveness * 0
        damage_result: int = 1 if math.floor(damage) <= 1 else math.floor(damage * random.randint(217, 255) / 255)
        if move_result:
            return move_result.set_damage_attack(is_critical=True if critical == 2 else False, type_effectiveness=type_effectiveness), damage_result
        return MoveResult(move.category, is_critical=True if critical == 2 else False, type_effectiveness=type_effectiveness), damage_result

    @staticmethod
    def stat_change(move: Move, target_pokemon: 'Pokemon', move_result: MoveResult = None) -> MoveResult:
        stat_change_list: list = []
        for i in range(len(move.stat_changes)):
            stat_change: int = 0
            if move.stat_changes[i]['change'] > 0 and target_pokemon.stats_effect[move.stat_changes[i]['stat']] == 6:
                stat_change = 9
            elif move.stat_changes[i]['change'] < 0 and target_pokemon.stats_effect[move.stat_changes[i]['stat']] == -6:
                stat_change = 10
            elif target_pokemon.stats_effect[move.stat_changes[i]['stat']] + move.stat_changes[i]['change'] >= 6:
                target_pokemon.stats_effect[move.stat_changes[i]['stat']] = 6
                stat_change = 4
            else:
                target_pokemon.stats_effect[move.stat_changes[i]['stat']] += move.stat_changes[i]['change']
                if target_pokemon.stats_effect[move.stat_changes[i]['stat']] > 6:
                    target_pokemon.stats_effect[move.stat_changes[i]['stat']] = 6
                elif target_pokemon.stats_effect[move.stat_changes[i]['stat']] < -6:
                    target_pokemon.stats_effect[move.stat_changes[i]['stat']] = -6
                match move.stat_changes[i]['change']:
                    case 1:
                        stat_change = 1
                    case 2:
                        stat_change = 2
                    case 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11:
                        stat_change = 3
                    case -1:
                        stat_change = 6
                    case -2:
                        stat_change = 7
                    case -3 | -4 | -5 | -6 | -7 | -8 | -9 | -10 | -11:
                        stat_change = 8
                    case _:
                        raise Exception(f'not define this {stat_change=}')
            stat_data: dict = util.fetch_json('stat', str(move.stat_changes[i]["stat"]))
            stat_change_list.append((stat_data['name'].upper(), stat_change))
        if move_result:
            return move_result.set_stat_change(stat_change_target=target_pokemon, stat_change_list=stat_change_list)
        return MoveResult(move.category, stat_change_target=target_pokemon, stat_change_list=stat_change_list)

    @staticmethod
    def stat_accuracy(stat_chance: int) -> bool:
        if stat_chance == 0:
            return True
        r: int = random.randint(1, 100)
        return True if r <= stat_chance else False

    @staticmethod
    def attack_accuracy(attack_pokemon: 'Pokemon', move: Move, defender_pokemon: 'Pokemon') -> bool:
        if not move.accuracy:
            return True
        b: int = math.floor(move.accuracy * 255 / 100)
        c: float = attack_pokemon.get_stat_effect(7)
        d: float = defender_pokemon.get_stat_effect(8)
        a: float = b * c / d
        r: int = random.randint(1, 255)
        if move.category == 9:
            for pokemon_type in defender_pokemon.types:
                if util.type_in_pokemon(util.fetch_json('type', str(move.type))['damage_relations']['no_damage_to'], pokemon_type):
                    return False
            if attack_pokemon.stats[6] < defender_pokemon.stats[6]:
                return False
            return True if r < b else False
        return True if r < a else False
