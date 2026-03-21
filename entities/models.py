# -*- coding: utf-8 -*-
"""
entities/models.py
プロジェクトで使う「登場人物データ」をここに集約する。
- mainやfieldやbattleは、ここにある型を使うだけ（中身を増やしても影響が局所化する）
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Stats:
    """戦闘に必要な数値。レベル上げ無しでも成立する最小セット。"""
    max_hp: int
    attack: int
    defense: int = 0

    def clamp_hp(self, hp: int) -> int:
        return max(0, min(self.max_hp, hp))


@dataclass
class Character:
    """プレイヤー/敵の共通部分。"""
    name: str
    stats: Stats
    hp: int

    @property
    def is_dead(self) -> bool:
        return self.hp <= 0

    def heal_full(self) -> None:
        self.hp = self.stats.max_hp

    def take_damage(self, dmg: int) -> int:
        """実際に減ったHP量を返す（0未満にならない）。"""
        dmg = max(0, int(dmg))
        before = self.hp
        self.hp = self.stats.clamp_hp(self.hp - dmg)
        return before - self.hp


@dataclass
class Player(Character):
    """主人公。必要なら所持金や所持品を後で足せる。"""
    pass


@dataclass
class Enemy(Character):
    """敵。行動AIの種類などを後で足せる。"""
    ai_type: str = "basic"
