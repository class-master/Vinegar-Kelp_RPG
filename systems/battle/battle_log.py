# systems/battle/battle_log.py
from typing import TypedDict, Literal


Target = Literal["player", "enemy"]
EventType = Literal["attack", "damage", "critical", "defeat"]


class BattleLog(TypedDict):
    event: EventType
    attacker: Target | None
    target: Target | None
    damage: int | None
    critical: bool | None
    text: str