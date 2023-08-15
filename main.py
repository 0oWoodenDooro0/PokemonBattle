import random
from pprint import pprint

import pygame as pg

import constants as const
import util
from button import Button
from pokemon import Pokemon
from state import BattleState, AttackState

TITLE = "Pokemon Battle"
FPS = 60

pg.init()

clock = pg.time.Clock()

screen = pg.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
pg.display.set_caption(TITLE)

TEXT_FONT = pg.font.Font('assets/joystix monospace.otf', 20)

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
front_pokemon = Pokemon(data, front=True)

data = util.fetch_json('pokemon/pokemon1.json')
back_pokemon = Pokemon(data)

fight_button_image = pg.image.load('assets/button/fight_button.png').convert_alpha()
bag_button_image = pg.image.load('assets/button/bag_button.png').convert_alpha()
pokemon_button_image = pg.image.load('assets/button/pokemon_button.png').convert_alpha()
run_button_image = pg.image.load('assets/button/run_button.png').convert_alpha()
empty_button_image = pg.image.load('assets/button/btn.png').convert_alpha()

fight_button = Button(const.PANEL_WIDTH + (const.SCREEN_WIDTH - const.PANEL_WIDTH) // 4, const.SCREEN_HEIGHT - const.PANEL_HEIGHT * 3 // 4, fight_button_image, center=True)
bag_button = Button(const.PANEL_WIDTH + (const.SCREEN_WIDTH - const.PANEL_WIDTH) * 3 // 4, const.SCREEN_HEIGHT - const.PANEL_HEIGHT * 3 // 4, bag_button_image, center=True)
pokemon_button = Button(const.PANEL_WIDTH + (const.SCREEN_WIDTH - const.PANEL_WIDTH) // 4, const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4, pokemon_button_image, center=True)
run_button = Button(const.PANEL_WIDTH + (const.SCREEN_WIDTH - const.PANEL_WIDTH) * 3 // 4, const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4, run_button_image, center=True)

move_buttons = []
for i in range(4):
    x = const.PANEL_WIDTH // 4 * (1 if i % 2 == 0 else 3)
    y = const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4 * (3 if i // 2 == 0 else 1)
    move_button = Button(x, y, empty_button_image, check_mouse_on=True, center=True)
    move_buttons.append(move_button)

battle_state: BattleState = BattleState.PREBATTLE
attack_state: AttackState = AttackState.FIRST_ATTACK
back_move: dict | None = None
front_move: dict | None = None
first_move: dict | None = None
first_pokemon: Pokemon | None = None
last_move: dict | None = None
last_pokemon: Pokemon | None = None
type_effectiveness: int | float | None = None
stat_change_list: list | None = None
stat_change_num: int = 0

run = True
while run:
    clock.tick(FPS)

    screen.fill(const.GREY)
    screen.blit(panel, panel_rect)
    screen.blit(back_value_image, back_value_image_rect)
    screen.blit(front_value_image, front_value_image_rect)
    front_pokemon.draw(screen)
    back_pokemon.draw(screen)

    util.draw_text(front_pokemon.name, TEXT_FONT, const.BLACK, (const.FRONT_VALUE_POS[0] - 80, const.FRONT_VALUE_POS[1] - 40), screen, True)
    util.draw_text(f'Lv {front_pokemon.level}', TEXT_FONT, const.BLACK, (const.FRONT_VALUE_POS[0] + 70, const.FRONT_VALUE_POS[1] - 40), screen, True)
    util.draw_text(back_pokemon.name, TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] - 80 + 64, const.BACK_VALUE_POS[1] - 40), screen, True)
    util.draw_text(f'Lv {back_pokemon.level}', TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] + 70 + 64, const.BACK_VALUE_POS[1] - 40), screen, True)
    util.draw_text(f'{back_pokemon.hp}/{back_pokemon.stats[1]}', TEXT_FONT, const.BLACK, (const.BACK_VALUE_POS[0] + 70, const.BACK_VALUE_POS[1] + 40), screen, True)

    if fight_button.draw(screen) and battle_state != BattleState.ATTACK:
        battle_state = BattleState.FIGHT
    if bag_button.draw(screen):
        pass
    if pokemon_button.draw(screen):
        pass
    if run_button.draw(screen):
        run = False

    match battle_state:
        case BattleState.PREBATTLE:
            util.draw_text('What will', TEXT_FONT, const.BLACK, (20, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + 20), screen)
            util.draw_text(f'{back_pokemon.name} do?', TEXT_FONT, const.BLACK, (20, const.SCREEN_HEIGHT - const.PANEL_HEIGHT + 60), screen)

        case BattleState.FIGHT:
            for i in range(len(back_pokemon.moves)):
                x = const.PANEL_WIDTH // 4 * (1 if i % 2 == 0 else 3)
                y = const.SCREEN_HEIGHT - const.PANEL_HEIGHT // 4 * (3 if i // 2 == 0 else 1) - 20
                util.draw_text(f'{back_pokemon.moves[i]["name"]}', TEXT_FONT, const.BLACK, (x, y), screen, True)
                util.draw_text(f'{back_pokemon.moves[i]["pp"]}/{back_pokemon.moves[i]["max_pp"]}', TEXT_FONT, const.BLACK, (x, y + 40), screen, True)
                button_click = move_buttons[i].draw(screen)
                if button_click[0]:
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
                    screen.blit(attribute_panel, attribute_panel_rect)

        case BattleState.ATTACK:
            move_panel.fill(const.WHITE)
            match attack_state:
                case AttackState.FIRST_ATTACK:
                    if first_pokemon.attack_accuracy(first_move, last_pokemon):
                        attack_state = AttackState.FIRST_ATTACK_HIT
                        type_effectiveness, stat_change_list = first_pokemon.attack(first_move, last_pokemon)
                        if stat_change_list:
                            stat_change_num = len(stat_change_list)
                    else:
                        attack_state = AttackState.FIRST_ATTACK_NOT_HIT
                case AttackState.FIRST_ATTACK_HIT:
                    util.draw_text(f'{first_pokemon.name} used', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                    util.draw_text(f'{first_move["name"]}', TEXT_FONT, const.BLACK, (20, 60), move_panel)
                case AttackState.FIRST_EFFECTIVE:
                    match type_effectiveness:
                        case 2:
                            util.draw_text(f"It's super effective!", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                        case 0.5:
                            util.draw_text(f"It's not very", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            util.draw_text(f'effective...', TEXT_FONT, const.BLACK, (20, 60), move_panel)
                        case 0:
                            util.draw_text(f"It's not effective...", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                        case 1 | None:
                            attack_state = AttackState.FIRST_STAT_CHANGE
                case AttackState.FIRST_STAT_CHANGE:
                    if stat_change_num == 0 or not stat_change_list:
                        attack_state = AttackState.LAST_ATTACK
                    else:
                        match stat_change_list[stat_change_num - 1]:
                            case (target_pokemon, stat_name, 1):
                                util.draw_text(f'{target_pokemon.name} {stat_name} rose!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 2):
                                util.draw_text(f'{target_pokemon.name} {stat_name} rose sharply!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 3):
                                util.draw_text(f'{target_pokemon.name} {stat_name} rose drastically!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 4):
                                util.draw_text(f'{target_pokemon.name} maxed its {stat_name}!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 6):
                                util.draw_text(f'{target_pokemon.name} {stat_name} fell!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 7):
                                util.draw_text(f'{target_pokemon.name} {stat_name} harshly fell!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 8):
                                util.draw_text(f'{target_pokemon.name} {stat_name} severely fell!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 9):
                                util.draw_text(f"{target_pokemon.name} {stat_name} won't go any higher!", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 10):
                                util.draw_text(f"{target_pokemon.name} {stat_name} won't go any lower!", TEXT_FONT, const.BLACK, (20, 20), move_panel)

                case AttackState.FIRST_ATTACK_NOT_HIT:
                    util.draw_text(f'{last_pokemon.name}', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                    util.draw_text(f'avoided the attack', TEXT_FONT, const.BLACK, (20, 60), move_panel)
                case AttackState.LAST_ATTACK:
                    if last_pokemon.attack_accuracy(last_move, first_pokemon):
                        attack_state = AttackState.LAST_ATTACK_HIT
                        type_effectiveness, stat_change_list = last_pokemon.attack(last_move, first_pokemon)
                        if stat_change_list:
                            stat_change_num = len(stat_change_list)
                    else:
                        attack_state = AttackState.LAST_ATTACK_NOT_HIT
                case AttackState.LAST_ATTACK_HIT:
                    util.draw_text(f'{last_pokemon.name} used', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                    util.draw_text(f'{last_move["name"]}', TEXT_FONT, const.BLACK, (20, 60), move_panel)
                case AttackState.LAST_EFFECTIVE:
                    match type_effectiveness:
                        case 2:
                            util.draw_text(f"It's super effective!", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                        case 0.5:
                            util.draw_text(f"It's not very", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            util.draw_text(f"effective...", TEXT_FONT, const.BLACK, (20, 60), move_panel)
                        case 0:
                            util.draw_text(f"It's not effective...", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                        case 1 | None:
                            attack_state = AttackState.LAST_STAT_CHANGE
                case AttackState.LAST_ATTACK_NOT_HIT:
                    util.draw_text(f'{first_pokemon.name}', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                    util.draw_text(f'avoided the attack', TEXT_FONT, const.BLACK, (20, 60), move_panel)
                case AttackState.LAST_STAT_CHANGE:
                    if stat_change_num == 0 or not stat_change_list:
                        battle_state = BattleState.PREBATTLE
                    else:
                        match stat_change_list[stat_change_num - 1]:
                            case (target_pokemon, stat_name, 1):
                                util.draw_text(f'{target_pokemon.name} {stat_name} rose!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 2):
                                util.draw_text(f'{target_pokemon.name} {stat_name} rose sharply!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 3):
                                util.draw_text(f'{target_pokemon.name} {stat_name} rose drastically!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 4):
                                util.draw_text(f'{target_pokemon.name} maxed its {stat_name}!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 6):
                                util.draw_text(f'{target_pokemon.name} {stat_name} fell!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 7):
                                util.draw_text(f'{target_pokemon.name} {stat_name} harshly fell!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 8):
                                util.draw_text(f'{target_pokemon.name} {stat_name} severely fell!', TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 9):
                                util.draw_text(f"{target_pokemon.name} {stat_name} won't go any higher!", TEXT_FONT, const.BLACK, (20, 20), move_panel)
                            case (target_pokemon, stat_name, 10):
                                util.draw_text(f"{target_pokemon.name} {stat_name} won't go any lower!", TEXT_FONT, const.BLACK, (20, 20), move_panel)

            screen.blit(move_panel, move_panel_rect)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            match attack_state:
                case AttackState.FIRST_ATTACK_HIT:
                    attack_state = AttackState.FIRST_EFFECTIVE
                case AttackState.FIRST_EFFECTIVE:
                    attack_state = AttackState.LAST_ATTACK
                case AttackState.FIRST_ATTACK_NOT_HIT:
                    attack_state = AttackState.LAST_ATTACK
                case AttackState.LAST_ATTACK_HIT:
                    attack_state = AttackState.LAST_EFFECTIVE
                case AttackState.LAST_EFFECTIVE:
                    battle_state = BattleState.PREBATTLE
                case AttackState.LAST_ATTACK_NOT_HIT:
                    battle_state = BattleState.PREBATTLE
                case AttackState.FIRST_STAT_CHANGE | AttackState.LAST_STAT_CHANGE:
                    stat_change_num -= 1

    pg.display.flip()
