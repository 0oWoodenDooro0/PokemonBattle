import random

import pygame as pg

import constants as const
import util
from button import Button
from pokemon import Pokemon
from state import BattleState, AttackState

TITLE = "Pokemon Battle"
FPS = 60

pg.init()
pg.mixer.init()

clock = pg.time.Clock()

screen = pg.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
pg.display.set_caption(TITLE)

TEXT_FONT = pg.font.Font('assets/pokemon_pixel_font.ttf', 40)
MESSAGE_FONT = pg.font.Font('assets/pokemon_pixel_font.ttf', 60)

panel = pg.Surface((const.SCREEN_WIDTH, const.PANEL_HEIGHT))
panel.fill(const.WHITE)
pg.draw.line(panel, const.BLACK, (0, 0), (const.SCREEN_WIDTH, 0), 2)
pg.draw.line(panel, const.BLACK, (0, 0), (const.SCREEN_WIDTH, 0), 2)
pg.draw.line(panel, const.BLACK, (const.PANEL_WIDTH, 0), (const.PANEL_WIDTH, const.PANEL_HEIGHT), 2)
pg.draw.line(panel, const.BLACK, (const.PANEL_WIDTH + 20, const.PANEL_HEIGHT // 2), (const.SCREEN_WIDTH - 20, const.PANEL_HEIGHT // 2), 1)
pg.draw.line(panel, const.BLACK, ((const.SCREEN_WIDTH + const.PANEL_WIDTH) // 2, 20), ((const.SCREEN_WIDTH + const.PANEL_WIDTH) // 2, const.PANEL_HEIGHT - 20), 1)
panel_rect = panel.get_rect()
panel_rect.topleft = (0, const.SCREEN_HEIGHT - const.PANEL_HEIGHT)
front_value_image = pg.image.load('assets/image/front_value.png').convert_alpha()
back_value_image = pg.image.load('assets/image/back_value.png').convert_alpha()
front_value_image_rect = front_value_image.get_rect()
back_value_image_rect = back_value_image.get_rect()
front_value_image_rect.center = const.FRONT_VALUE_POS
back_value_image_rect.center = const.BACK_VALUE_POS

attribute_panel = pg.Surface((const.SCREEN_WIDTH - const.PANEL_WIDTH - 4, const.PANEL_HEIGHT - 4))
attribute_panel.fill(const.WHITE)
attribute_panel_rect = attribute_panel.get_rect()
attribute_panel_rect.topleft = (const.PANEL_WIDTH + 2, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + 2)

move_panel = pg.Surface((const.PANEL_WIDTH - 4, const.PANEL_HEIGHT - 4))
move_panel.fill(const.WHITE)
move_panel_rect = move_panel.get_rect()
move_panel_rect.topleft = (0, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + 2)

data = util.fetch_json('pokemon/pokemon3.json')
front_pokemon = Pokemon(data, enemy=True)

data = util.fetch_json('pokemon/pokemon1.json')
back_pokemon = Pokemon(data)

selection_image = pg.image.load('assets/button/selection_button.png').convert_alpha()
move_button_image = pg.image.load('assets/button/move_button.png').convert_alpha()

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
back_move: dict | None = None
front_move: dict | None = None
first_move: dict | None = None
first_pokemon: Pokemon | None = None
last_move: dict | None = None
last_pokemon: Pokemon | None = None
critical: int | None = None
type_effectiveness: int | float | None = None
stat_change_list: list | None = None
stat_change_num: int = 0

pg.mixer.music.load('soundtrack/Wild Battle Music EXTENDED (128 kbps).mp3')
pg.mixer.music.set_volume(0.1)
pg.mixer.music.play(loops=-1)

run = True
while run:
    clock.tick(FPS)

    screen.fill(const.GREY)
    move_panel.fill(const.WHITE)
    attribute_panel.fill(const.WHITE)

    screen.blit(panel, panel_rect)
    screen.blit(back_value_image, back_value_image_rect)
    screen.blit(front_value_image, front_value_image_rect)
    front_pokemon.draw(screen)
    back_pokemon.draw(screen)

    util.draw_text(front_pokemon.name, TEXT_FONT, const.BLACK, (const.FRONT_VALUE_POS[0] - 150, const.FRONT_VALUE_POS[1] - 50), screen)
    util.draw_text(f'Lv{front_pokemon.level}', TEXT_FONT, const.BLACK, (const.FRONT_VALUE_POS[0] + 40, const.FRONT_VALUE_POS[1] - 50), screen)
    util.draw_text(back_pokemon.name, TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] - 150 + 64, const.BACK_VALUE_POS[1] - 50), screen)
    util.draw_text(f'Lv{back_pokemon.level}', TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] + 40 + 64, const.BACK_VALUE_POS[1] - 50), screen)
    util.draw_text(f'{back_pokemon.hp}/{back_pokemon.stats[1]}', TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] + 70, const.BACK_VALUE_POS[1] + 40), screen, True)

    for i in range(4):
        x = (const.SCREEN_WIDTH - const.PANEL_WIDTH) // 4 * (1 if i % 2 == 0 else 3)
        y = const.PANEL_HEIGHT // 4 * (1 if i // 2 == 0 else 3)
        util.draw_text(selection_button_texts[i], TEXT_FONT, const.BLACK, (x, y), attribute_panel, center=True)
        if selection_buttons[i].draw(screen) and battle_state != BattleState.ATTACK:
            match i:
                case 0:
                    battle_state = BattleState.FIGHT
                case 1:
                    pass
                case 2:
                    pass
                case 3:
                    run = False

    match battle_state:

        case BattleState.PREBATTLE:
            util.draw_text('What will', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
            util.draw_text(f'{back_pokemon.name} do?', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

        case BattleState.FIGHT:
            for i in range(len(back_pokemon.moves)):
                x = const.PANEL_WIDTH // 4 * (1 if i % 2 == 0 else 3)
                y = const.PANEL_HEIGHT // 4 * (1 if i // 2 == 0 else 3) - 20
                util.draw_text(f'{back_pokemon.moves[i]["name"]}', TEXT_FONT, const.BLACK, (x, y), move_panel, True)
                util.draw_text(f'{back_pokemon.moves[i]["pp"]}/{back_pokemon.moves[i]["max_pp"]}', TEXT_FONT, const.BLACK, (x, y + 40), move_panel, True)
                button_click = move_buttons[i].draw(screen)
                if button_click[0] and back_pokemon.moves[i]['pp'] != 0:
                    back_move = back_pokemon.moves[i]
                    front_move = random.choice(front_pokemon.moves)
                    if back_move['priority'] > front_move['priority']:
                        first_move = back_move
                        first_pokemon = back_pokemon
                        last_move = front_move
                        last_pokemon = front_pokemon
                    elif back_move['priority'] < front_move['priority']:
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
                    battle_state = BattleState.ATTACK
                    attack_state = AttackState.FIRST_ATTACK
                elif button_click[1]:
                    attribute_panel.fill(const.WHITE)
                    util.draw_text(f'Power: {back_pokemon.moves[i]["power"]}', TEXT_FONT, const.BLACK, (20, 20), attribute_panel)
                    util.draw_text(f'Accuracy: {back_pokemon.moves[i]["accuracy"]}', TEXT_FONT, const.BLACK, (20, 60), attribute_panel)
                    type_name = util.fetch_json(f'type/{back_pokemon.moves[i]["type"]}.json')['name']
                    util.draw_text(f'Type: {type_name}', TEXT_FONT, const.BLACK, (20, 100), attribute_panel)

        case BattleState.DEFEAT:
            if front_pokemon.hp == 0:
                isEnemy = 'Enemy ' if front_pokemon.enemy else ''
                util.draw_text(f'{isEnemy}{front_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                util.draw_text(f'fainted!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
            elif back_pokemon.hp == 0:
                isEnemy = 'Enemy ' if back_pokemon.enemy else ''
                util.draw_text(f'{isEnemy}{back_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                util.draw_text(f'fainted!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
            screen.blit(move_panel, move_panel_rect)

        case BattleState.EXP:
            util.draw_text(f'{back_pokemon.name} gained', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
            util.draw_text(f'{util.get_battle_experience(front_pokemon)} EXP. Points!', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)
            screen.blit(move_panel, move_panel_rect)

        case BattleState.ATTACK:
            match attack_state:
                case AttackState.FIRST_ATTACK:
                    if first_pokemon.attack_accuracy(first_move, last_pokemon):
                        critical, type_effectiveness, stat_change_list = first_pokemon.attack(first_move, last_pokemon)
                        if stat_change_list:
                            stat_change_num = len(stat_change_list)
                        attack_state = AttackState.FIRST_ATTACK_HIT
                    else:
                        attack_state = AttackState.FIRST_ATTACK_NOT_HIT

                case AttackState.FIRST_ATTACK_HIT:
                    isEnemy = 'Enemy ' if first_pokemon.enemy else ''
                    util.draw_text(f'{isEnemy}{first_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                    util.draw_text(f'used {first_move["name"]}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

                case AttackState.FIRST_CRICAL_HIT:
                    util.draw_text(f"Critical Hit!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)

                case AttackState.FIRST_EFFECTIVE:
                    match type_effectiveness:
                        case 2:
                            util.draw_text(f"It's super effective!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                        case 0.5:
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
                        if stat_change_list:
                            stat_change_num = len(stat_change_list)
                        attack_state = AttackState.LAST_ATTACK_HIT
                    else:
                        attack_state = AttackState.LAST_ATTACK_NOT_HIT

                case AttackState.LAST_ATTACK_HIT:
                    isEnemy = 'Enemy ' if last_pokemon.enemy else ''
                    util.draw_text(f'{isEnemy}{last_pokemon.name}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                    util.draw_text(f'used {last_move["name"]}', MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_2, move_panel, mid_left=True)

                case AttackState.LAST_CRICAL_HIT:
                    util.draw_text(f"Critical Hit!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)

                case AttackState.LAST_EFFECTIVE:
                    match type_effectiveness:
                        case 2:
                            util.draw_text(f"It's super effective!", MESSAGE_FONT, const.BLACK, const.MESSAGE_POS_LINE_1, move_panel, mid_left=True)
                        case 0.5:
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
                    if stat_change_num == 0 or not stat_change_list:
                        battle_state = BattleState.PREBATTLE
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

    screen.blit(move_panel, move_panel_rect)
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
                    attack_state = AttackState.LAST_ATTACK
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
                    battle_state = BattleState.PREBATTLE
                case AttackState.LAST_ATTACK_NOT_HIT:
                    battle_state = BattleState.PREBATTLE
                case AttackState.FIRST_STAT_CHANGE | AttackState.LAST_STAT_CHANGE:
                    stat_change_num -= 1
            if battle_state == BattleState.DEFEAT:
                back_pokemon.add_experience(util.get_battle_experience(front_pokemon))
                battle_state = BattleState.EXP

    pg.display.flip()
