import math
import random

import util
from move import Move
from move_result import MoveResult
from pokemon import Pokemon
from state import BattleState, AttackState


class Battle:
    def __init__(self, front_pokemon, back_pokemon):
        self.front_pokemon: Pokemon = front_pokemon
        self.back_pokemon: Pokemon = back_pokemon
        self.battle_state: BattleState = BattleState.PREBATTLE
        self.attack_state: AttackState = AttackState.FIRST_ATTACK

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
                move_result, damage = self.damage_attack(attck_pokemon,move, defender_pokemon)
                defender_pokemon.hp -= damage
                if self.stat_accuracy(move.stat_chance):
                    return self.stat_change(move, defender_pokemon, move_result)
                return move_result
            case 7:
                move_result, damage = self.damage_attack(attck_pokemon,move, defender_pokemon)
                defender_pokemon.hp -= damage
                if self.stat_accuracy(move.stat_chance):
                    return self.stat_change(move, attck_pokemon, move_result)
                return move_result
            case 8:
                move_result, damage = self.damage_attack(attck_pokemon,move, defender_pokemon)
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
