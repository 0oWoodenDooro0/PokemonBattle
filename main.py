import os.path
import random

import pygame as pg

import constants as const
import util
from button import Button
from move import Move
from pokemon import Pokemon
from state import BattleState, AttackState
from generation import Generation

TITLE = "Pokemon Battle"
FPS = 60

pg.mixer.pre_init()
pg.mixer.init()
pg.init()

clock = pg.time.Clock()

screen = pg.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
pg.display.set_caption(TITLE)

TEXT_FONT = pg.font.Font(os.path.join('assets', 'pokemon_pixel_font.ttf'), 40)
MESSAGE_FONT = pg.font.Font(os.path.join('assets', 'pokemon_pixel_font.ttf'), 60)

front_value_image = pg.image.load(os.path.join('assets', 'image', 'front_value.png')).convert_alpha()
back_value_image = pg.image.load(os.path.join('assets', 'image', 'back_value.png')).convert_alpha()
front_value_image_rect = front_value_image.get_rect()
back_value_image_rect = back_value_image.get_rect()
front_value_image_rect.center = const.FRONT_VALUE_POS
back_value_image_rect.center = const.BACK_VALUE_POS

attribute_panel = pg.Surface((const.SCREEN_WIDTH - const.PANEL_WIDTH, const.PANEL_HEIGHT))
attribute_panel_rect = attribute_panel.get_rect()
attribute_panel_rect.topleft = (const.PANEL_WIDTH, const.SCREEN_HEIGHT - const.PANEL_HEIGHT)

move_panel = pg.Surface((const.PANEL_WIDTH, const.PANEL_HEIGHT))
move_panel_rect = move_panel.get_rect()
move_panel_rect.topleft = (0, const.SCREEN_HEIGHT - const.PANEL_HEIGHT)

generation = Generation(1)

front_pokemon = Pokemon(1, generation, enemy=True)

back_pokemon = Pokemon(64, generation)

selection_image = pg.image.load(os.path.join('assets', 'button', 'selection_button.png')).convert_alpha()
move_button_image = pg.image.load(os.path.join('assets', 'button', 'move_button.png')).convert_alpha()

selection_buttons: list[Button] = []
selection_button_texts: list[str] = ['FIGHT', 'BAG', 'POKEMON', 'RUN']
for i in range(4):
    x = const.PANEL_WIDTH + (const.SCREEN_WIDTH - const.PANEL_WIDTH) // 4 * (1 if i % 2 == 0 else 3)
    y = const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4 * (3 if i // 2 == 0 else 1)
    selection_button = Button((x, y), selection_image, center=True)
    selection_buttons.append(selection_button)

move_buttons: list[Button] = []
for i in range(4):
    x = const.PANEL_WIDTH // 4 * (1 if i % 2 == 0 else 3)
    y = const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4 * (3 if i // 2 == 0 else 1)
    move_button = Button((x, y), move_button_image, check_mouse_on=True, center=True)
    move_buttons.append(move_button)

battle_state: BattleState = BattleState.PREBATTLE
attack_state: AttackState = AttackState.FIRST_ATTACK
back_move: Move | None = None
front_move: Move | None = None
first_move: Move | None = None
first_pokemon: Pokemon | None = None
last_move: Move | None = None
last_pokemon: Pokemon | None = None
critical: int | None = None
type_effectiveness: int | float | None = None
stat_change_list: list | None = None
stat_change_num: int = 0
damage_time: list[int, int] = [0, 0]

pg.mixer.music.load(os.path.join('soundtrack', 'Battle Music.mp3'))
pg.mixer.music.set_volume(0.1)
pg.mixer.music.play(loops=-1)

button_select_sound = pg.mixer.Sound(os.path.join('sound_effect', 'Button Select.wav'))
hurt_sound = pg.mixer.Sound(os.path.join('sound_effect', 'Hurt.wav'))

run = True
while run:
    clock.tick(FPS)

    screen.fill(const.GREY)
    move_panel.fill(const.WHITE)
    attribute_panel.fill(const.WHITE)
    # print(battle_state, attack_state)

    if battle_state is not BattleState.PREBATTLE:
        screen.blit(back_value_image, back_value_image_rect)
        screen.blit(front_value_image, front_value_image_rect)
        front_pokemon.draw_health_bar(screen)
        back_pokemon.draw_health_bar(screen)

        util.draw_text(front_pokemon.name, TEXT_FONT, const.BLACK, (const.FRONT_VALUE_POS[0] - 150, const.FRONT_VALUE_POS[1] - 50), screen)
        util.draw_text(f'Lv{front_pokemon.level}', TEXT_FONT, const.BLACK, (const.FRONT_VALUE_POS[0] + 40, const.FRONT_VALUE_POS[1] - 50), screen)
        util.draw_text(back_pokemon.name, TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] - 150 + 64, const.BACK_VALUE_POS[1] - 50), screen)
        util.draw_text(f'Lv{back_pokemon.level}', TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] + 40 + 64, const.BACK_VALUE_POS[1] - 50), screen)
        util.draw_text(f'{back_pokemon.hp}/{back_pokemon.stats[1]}', TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] + 70, const.BACK_VALUE_POS[1] + 40), screen, True)

    if battle_state is BattleState.SELECTION or battle_state is BattleState.FIGHT:
        pg.draw.line(screen, const.BLACK, (const.PANEL_WIDTH, const.SCREEN_HEIGHT - const.PANEL_HEIGHT), (const.PANEL_WIDTH, const.SCREEN_HEIGHT), 2)
        for i in range(4):
            x = (const.SCREEN_WIDTH - const.PANEL_WIDTH) // 4 * (1 if i % 2 == 0 else 3)
            y = const.PANEL_HEIGHT // 4 * (1 if i // 2 == 0 else 3)
            util.draw_text(selection_button_texts[i], TEXT_FONT, const.BLACK, (x, y), attribute_panel, center=True)
            if selection_buttons[i].draw(screen) and battle_state != BattleState.ATTACK:
                button_select_sound.play()
                match i:
                    case 0:
                        battle_state = BattleState.FIGHT
                    case 1:
                        pass
                    case 2:
                        pass
                    case 3:
                        run = False

    if damage_time[0] % 20 < 10 or damage_time[0] > 60:
        front_pokemon.draw(screen)
    if damage_time[1] % 20 < 10 or damage_time[1] > 60:
        back_pokemon.draw(screen)

    match battle_state:

        case BattleState.PREBATTLE:
            if front_pokemon.sprite_rect.right != const.SCREEN_WIDTH and back_pokemon.sprite_rect.left != 0:
                front_pokemon.sprite_rect.right += 5
                back_pokemon.sprite_rect.left -= 5
            else:
                battle_state = BattleState.SELECTION

        case BattleState.SELECTION:
            util.draw_text('What will', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
            util.draw_text(f'{back_pokemon.name} do?', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

        case BattleState.FIGHT:
            for i in range(len(back_pokemon.moves)):
                x = const.PANEL_WIDTH // 4 * (1 if i % 2 == 0 else 3)
                y = const.PANEL_HEIGHT // 4 * (1 if i // 2 == 0 else 3) - 20
                util.draw_text(f'{back_pokemon.moves[i].name}', TEXT_FONT, const.BLACK, (x, y), move_panel, True)
                util.draw_text(f'{back_pokemon.moves[i].pp}/{back_pokemon.moves[i].max_pp}', TEXT_FONT, const.BLACK, (x, y + 40), move_panel, True)
                button_click = move_buttons[i].draw(screen)
                if button_click[0] and back_pokemon.moves[i].pp != 0:
                    button_select_sound.play()
                    back_move = back_pokemon.moves[i]
                    front_move = random.choice(front_pokemon.moves)
                    if back_move.priority > front_move.priority:
                        first_move = back_move
                        first_pokemon = back_pokemon
                        last_move = front_move
                        last_pokemon = front_pokemon
                    elif back_move.priority < front_move.priority:
                        first_move = back_move
                        first_pokemon = back_pokemon
                        last_move = front_move
                    else:
                        if back_pokemon.stats[6] >= front_pokemon.stats[6]:
                            first_move = back_move
                            first_pokemon = back_pokemon
                            last_move = front_move
                            last_pokemon = front_pokemon
                        else:
                            first_move = front_move
                            first_pokemon = front_pokemon
                            last_move = back_move
                            last_pokemon = back_pokemon
                    back_move.pp -= 1
                    battle_state = BattleState.ATTACK
                    attack_state = AttackState.FIRST_ATTACK
                    damage_time = [0, 0]
                elif button_click[1]:
                    attribute_panel.fill(const.WHITE)
                    util.draw_text(f'Power: {back_pokemon.moves[i].power}', TEXT_FONT, const.BLACK, (20, 20), attribute_panel)
                    util.draw_text(f'Accuracy: {back_pokemon.moves[i].accuracy}', TEXT_FONT, const.BLACK, (20, 60), attribute_panel)
                    type_name = util.fetch_json('type', str(back_pokemon.moves[i].type))['name'].capitalize()
                    util.draw_text(f'Type: {type_name}', TEXT_FONT, const.BLACK, (20, 100), attribute_panel)

        case BattleState.DEFEAT:
            damage_time = [0, 0]
            if front_pokemon.hp == 0:
                isEnemy = 'Enemy ' if front_pokemon.enemy else ''
                util.draw_text(f'{isEnemy}{front_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                util.draw_text(f'fainted!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
            elif back_pokemon.hp == 0:
                isEnemy = 'Enemy ' if back_pokemon.enemy else ''
                util.draw_text(f'{isEnemy}{back_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                util.draw_text(f'fainted!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

        case BattleState.EXP:
            util.draw_text(f'{back_pokemon.name} gained', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
            util.draw_text(f'{util.get_battle_experience(front_pokemon)} EXP. Points!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

        case BattleState.ATTACK:
            match attack_state:
                case AttackState.FIRST_ATTACK:
                    if first_pokemon.attack_accuracy(first_move, last_pokemon):
                        critical, type_effectiveness, stat_change_list = first_pokemon.attack(first_move, last_pokemon)
                        print(critical, type_effectiveness, stat_change_list)
                        if stat_change_list:
                            stat_change_num = len(stat_change_list)
                        if critical:
                            hurt_sound.play()
                        attack_state = AttackState.FIRST_ATTACK_HIT
                    else:
                        attack_state = AttackState.FIRST_ATTACK_NOT_HIT

                case AttackState.FIRST_ATTACK_HIT:
                    if critical:
                        damage_time[0 if last_pokemon.enemy else 1] += 1
                    isEnemy = 'Enemy ' if first_pokemon.enemy else ''
                    util.draw_text(f'{isEnemy}{first_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                    util.draw_text(f'used {first_move.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

                case AttackState.FIRST_CRICAL_HIT:
                    if critical:
                        damage_time[0 if last_pokemon.enemy else 1] += 1
                    util.draw_text(f"Critical Hit!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)

                case AttackState.FIRST_EFFECTIVE:
                    if critical:
                        damage_time[0 if last_pokemon.enemy else 1] += 1
                    match type_effectiveness:
                        case 2 | 4:
                            util.draw_text(f"It's super effective!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                        case 0.5 | 0.25:
                            util.draw_text(f"It's not very", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                            util.draw_text(f'effective...', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                        case 0:
                            util.draw_text(f"It's not effective...", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                        case 1 | None:
                            attack_state = AttackState.FIRST_STAT_CHANGE

                    if front_pokemon.hp == 0:
                        battle_state = BattleState.DEFEAT
                    elif back_pokemon.hp == 0:
                        battle_state = BattleState.DEFEAT

                case AttackState.FIRST_STAT_CHANGE:
                    damage_time = [0, 0]
                    if stat_change_num == 0 or not stat_change_list:
                        attack_state = AttackState.LAST_ATTACK
                    else:
                        match stat_change_list[stat_change_num - 1]:
                            case (target_pokemon, stat_name, 1):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} rose!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 2):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} rose sharply!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 3):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} rose drastically!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 4):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'maxed its {stat_name}!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 6):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} fell!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 7):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} harshly fell!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 8):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} severely fell!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 9):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f"{stat_name} won't go any higher!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 10):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f"{stat_name} won't go any lower!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

                case AttackState.FIRST_ATTACK_NOT_HIT:
                    isEnemy = 'Enemy ' if last_pokemon.enemy else ''
                    util.draw_text(f'{isEnemy}{last_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                    util.draw_text(f'avoided the attack', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

                case AttackState.LAST_ATTACK:
                    if last_pokemon.attack_accuracy(last_move, first_pokemon):
                        critical, type_effectiveness, stat_change_list = last_pokemon.attack(last_move, first_pokemon)
                        print(critical, type_effectiveness, stat_change_list)
                        if stat_change_list:
                            stat_change_num = len(stat_change_list)
                        if critical:
                            hurt_sound.play()
                        attack_state = AttackState.LAST_ATTACK_HIT
                    else:
                        attack_state = AttackState.LAST_ATTACK_NOT_HIT

                case AttackState.LAST_ATTACK_HIT:
                    if critical:
                        damage_time[0 if first_pokemon.enemy else 1] += 1
                    isEnemy = 'Enemy ' if last_pokemon.enemy else ''
                    util.draw_text(f'{isEnemy}{last_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                    util.draw_text(f'used {last_move.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

                case AttackState.LAST_CRICAL_HIT:
                    if critical:
                        damage_time[0 if first_pokemon.enemy else 1] += 1
                    util.draw_text(f"Critical Hit!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)

                case AttackState.LAST_EFFECTIVE:
                    if critical:
                        damage_time[0 if first_pokemon.enemy else 1] += 1
                    match type_effectiveness:
                        case 2 | 4:
                            util.draw_text(f"It's super effective!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                        case 0.5 | 0.25:
                            util.draw_text(f"It's not very", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                            util.draw_text(f"effective...", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                        case 0:
                            util.draw_text(f"It's not effective...", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                        case 1 | None:
                            attack_state = AttackState.LAST_STAT_CHANGE

                    if front_pokemon.hp == 0:
                        battle_state = BattleState.DEFEAT
                    elif back_pokemon.hp == 0:
                        battle_state = BattleState.DEFEAT

                case AttackState.LAST_STAT_CHANGE:
                    damage_time = [0, 0]
                    if stat_change_num == 0 or not stat_change_list:
                        battle_state = BattleState.SELECTION
                    else:
                        match stat_change_list[stat_change_num - 1]:
                            case (target_pokemon, stat_name, 1):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} rose!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 2):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} rose sharply!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 3):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} rose drastically!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 4):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'maxed its {stat_name}!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 6):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} fell!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 7):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} harshly fell!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 8):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f'{stat_name} severely fell!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 9):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f"{stat_name} won't go any higher!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
                            case (target_pokemon, stat_name, 10):
                                isEnemy = 'Enemy ' if target_pokemon.enemy else ''
                                util.draw_text(f'{isEnemy}{target_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                                util.draw_text(f"{stat_name} won't go any lower!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

                case AttackState.LAST_ATTACK_NOT_HIT:
                    isEnemy = 'Enemy ' if first_pokemon.enemy else ''
                    util.draw_text(f'{isEnemy}{first_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                    util.draw_text(f'avoided the attack', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

    pg.draw.line(move_panel, const.BLACK, (0, 0), (const.PANEL_WIDTH, 0), 2)
    pg.draw.line(move_panel, const.BLACK, (0, 0), (0, const.PANEL_HEIGHT), 2)
    screen.blit(move_panel, move_panel_rect)
    pg.draw.line(attribute_panel, const.BLACK, (0, 0), (const.SCREEN_WIDTH - const.PANEL_WIDTH, 0), 2)
    pg.draw.line(attribute_panel, const.BLACK, (0, 0), (0, const.PANEL_HEIGHT), 2)
    screen.blit(attribute_panel, attribute_panel_rect)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            match attack_state:
                case AttackState.FIRST_ATTACK_HIT:
                    if critical == 2:
                        attack_state = AttackState.FIRST_CRICAL_HIT
                    else:
                        attack_state = AttackState.FIRST_EFFECTIVE
                case AttackState.FIRST_CRICAL_HIT:
                    attack_state = AttackState.FIRST_EFFECTIVE
                case AttackState.FIRST_EFFECTIVE:
                    attack_state = AttackState.FIRST_STAT_CHANGE
                case AttackState.FIRST_ATTACK_NOT_HIT:
                    attack_state = AttackState.LAST_ATTACK
                case AttackState.LAST_ATTACK_HIT:
                    if critical == 2:
                        attack_state = AttackState.LAST_CRICAL_HIT
                    else:
                        attack_state = AttackState.LAST_EFFECTIVE
                case AttackState.LAST_CRICAL_HIT:
                    attack_state = AttackState.LAST_EFFECTIVE
                case AttackState.LAST_EFFECTIVE:
                    attack_state = AttackState.LAST_STAT_CHANGE
                case AttackState.LAST_ATTACK_NOT_HIT:
                    battle_state = BattleState.SELECTION
                case AttackState.FIRST_STAT_CHANGE | AttackState.LAST_STAT_CHANGE:
                    stat_change_num -= 1
            match battle_state:
                case BattleState.DEFEAT:
                    back_pokemon.add_experience(util.get_battle_experience(front_pokemon))
                    battle_state = BattleState.EXP
                case BattleState.EXP:
                    run = False

    pg.display.flip()
