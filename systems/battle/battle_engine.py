# systems/battle/battle_engine.py
# 戦闘の計算ロジックを管理するモジュールです。

import random

def player_attack(player, enemy):
    """
    プレイヤーが敵に攻撃した時のダメージ計算です。
    """
    # 基本ダメージ = 攻撃力 - 防御力（最低1ダメージ）
    base_damage = max(1, player.attack - enemy.defense)
    # 少しのランダム要素（乱数）を加えます
    actual_damage = base_damage + random.randint(0, 2)
    
    enemy.hp -= actual_damage
    if enemy.hp < 0:
        enemy.hp = 0
    return actual_damage

def enemy_attack(enemy, player):
    """
    敵がプレイヤーに攻撃した時のダメージ計算です。
    """
    base_damage = max(1, enemy.attack - player.defense)
    actual_damage = base_damage + random.randint(0, 1)
    
    player.hp -= actual_damage
    if player.hp < 0:
        player.hp = 0
    return actual_damage

class BattleEngine:
    """
    戦闘の1ターン進行を管理するクラス
    """

    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self._is_finished = False
        self._result = None

    def process_turn(self):
        # 1) player attack
        dmg = player_attack(self.player, self.enemy)
        log = f"{self.player.name}のこうげき！{self.enemy.name}に {dmg} ダメージ！"

        if self.enemy.hp <= 0:
            self._is_finished = True
            self._result = "player"
            return log

        # 2) enemy attack
        dmg2 = enemy_attack(self.enemy, self.player)
        log += f"\n{self.enemy.name}のこうげき！{self.player.name}は {dmg2} ダメージ！"

        if self.player.hp <= 0:
            self._is_finished = True
            self._result = "enemy"

        return log

    def is_finished(self):
        return self._is_finished

    def get_result(self):
        return self._result
