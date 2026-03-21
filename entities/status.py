# entities/status.py

class Status:
    """キャラクターの基本ステータス（純粋データモデル）"""

    def __init__(self, name: str, max_hp: int, attack: int, defense: int):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense

    # --- 状態判定 ---
    def is_alive(self) -> bool:
        return self.hp > 0

    # --- ダメージ処理 ---
    def take_damage(self, damage: int) -> None:
        self.hp = max(0, self.hp - damage)

    # --- 回復 ---
    def heal_full(self) -> None:
        self.hp = self.max_hp
