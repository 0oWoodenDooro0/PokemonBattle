import os.path

import pygame as pg

import constants as const
import util
from battle import Battle
from generation import Generation
from pokemon import Pokemon
from state import BattleState, AttackState

TITLE = "Pokemon Battle"
FPS = 60

pg.mixer.pre_init()
pg.mixer.init()
pg.init()

clock: pg.time.Clock = pg.time.Clock()

screen: pg.Surface = pg.display.set_mode((const.SCREEN_WIDTH, const.SCREEN_HEIGHT))
pg.display.set_caption(TITLE)

generation: Generation = Generation(1)

front_pokemon: Pokemon = Pokemon(7, generation, enemy=True)
back_pokemon: Pokemon = Pokemon(15, generation)
battle: Battle = Battle(front_pokemon, back_pokemon)

pg.mixer.music.load(os.path.join('soundtrack', 'Battle Music.mp3'))
pg.mixer.music.set_volume(0.05)
pg.mixer.music.play(loops=-1)

run: bool = True
while run:
    clock.tick(FPS)

    screen.fill(const.GREY)

    battle.update(screen, run)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            run = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            match battle.attack_state:
                case AttackState.FIRST_ATTACK_HIT:
                    print(f'{battle.attack_result.move_category=}')
                    match battle.attack_result.move_category:
                        case 2 | 6 | 7:
                            battle.attack_state = AttackState.FIRST_STAT_CHANGE
                        case 0 | 6 | 7 | 8 | 9:
                            if battle.attack_result.is_critical:
                                battle.attack_state = AttackState.FIRST_CRICAL_HIT
                            else:
                                battle.attack_state = AttackState.FIRST_EFFECTIVE
                case AttackState.FIRST_CRICAL_HIT:
                    battle.attack_state = AttackState.FIRST_EFFECTIVE
                case AttackState.FIRST_EFFECTIVE:
                    battle.attack_state = AttackState.FIRST_STAT_CHANGE
                case AttackState.FIRST_ATTACK_NOT_HIT:
                    battle.attack_state = AttackState.LAST_ATTACK
                case AttackState.LAST_ATTACK_HIT:
                    match battle.attack_result.move_category:
                        case 2 | 6 | 7:
                            battle.attack_state = AttackState.LAST_STAT_CHANGE
                        case 0 | 6 | 7 | 8 | 9:
                            if battle.attack_result.is_critical:
                                battle.attack_state = AttackState.LAST_CRICAL_HIT
                            else:
                                battle.attack_state = AttackState.LAST_EFFECTIVE
                case AttackState.LAST_CRICAL_HIT:
                    battle.attack_state = AttackState.LAST_EFFECTIVE
                case AttackState.LAST_EFFECTIVE:
                    battle.attack_state = AttackState.LAST_STAT_CHANGE
                case AttackState.LAST_ATTACK_NOT_HIT:
                    battle.battle_state = BattleState.SELECTION
                    battle.attack_state = AttackState.FIRST_ATTACK
                case AttackState.FIRST_STAT_CHANGE | AttackState.LAST_STAT_CHANGE:
                    battle.stat_change_num -= 1
            print(battle.battle_state, battle.attack_state)
            match battle.battle_state:
                case BattleState.DEFEAT:
                    battle.back_pokemon.add_experience(util.get_battle_experience(front_pokemon))
                    battle.battle_state = BattleState.EXP
                case BattleState.EXP:
                    run = False

    pg.display.flip()
