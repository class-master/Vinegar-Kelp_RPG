# systems/battle/battle_controller.py

from __future__ import annotations
import random
from typing import TypedDict, Literal, Optional
from entities.status import Status

Target = str

class BattleLog(TypedDict):
    text: str
    damage: int
    critical: bool
    target: Target


class BattleController:
    def __init__(self, player: Status, enemy: Status):
        self.player = player
        self.enemy = enemy
        self._winner: Optional[str] = None
        self._log_queue: list[BattleLog] = []

    def start(self) -> None:
        self._winner = None
        self._log_queue.clear()

    def _calc_damage(self, attacker: Status, defender: Status) -> tuple[int, bool]:
        base = max(1, attacker.attack - defender.defense)
        critical = (random.random() < 0.2)  # 20%
        if critical:
            base *= 2
        return base, critical

    def take_turn(self) -> None:
        if self.is_finished():
            return

        # --- プレイヤー攻撃 ---
        damage, critical = self._calc_damage(self.player, self.enemy)
        self.enemy.take_damage(damage)
        self._log_queue.append({
            "text": f"{self.player.name} のこうげき！ {damage} のダメージ！",
            "damage": damage,
            "critical": critical,
            "target": "enemy",
        })

        if not self.enemy.is_alive():
            self._winner = "player"
            return

        # --- 敵反撃 ---
        damage, critical = self._calc_damage(self.enemy, self.player)
        self.player.take_damage(damage)
        self._log_queue.append({
            "text": f"{self.enemy.name} のこうげき！ {damage} のダメージ！",
            "damage": damage,
            "critical": critical,
            "target": "player",
        })

        if not self.player.is_alive():
            self._winner = "enemy"

    # --- Viewが呼ぶ ---
    def has_log(self) -> bool:
        return len(self._log_queue) > 0

    def pop_log(self) -> BattleLog | None:
        if self._log_queue:
            return self._log_queue.pop(0)
        return None

    def is_finished(self) -> bool:
        return self._winner is not None

    def winner(self) -> str | None:
        return self._winner