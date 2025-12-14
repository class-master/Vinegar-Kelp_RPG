# -*- coding: utf-8 -*-
"""
Day6：アイテム使用ロジック（生徒用）

なぜ：
    「使う（use）」の処理を main_day6.py から分離して読みやすくするため。

前提：
    - inventory は {item_id: count} の辞書
    - player_status は {"hp": int, "max_hp": int} の辞書
    - items は items_day6.ITEMS を想定

入力：
    inventory, item_id, player_status, items

出力：
    (ok: bool, message: str)
    ok=True なら使用成功。

副作用：
    成功時、inventory の個数が減り、HPが増える。

例外：
    items に item_id がない場合は失敗扱い。
"""

def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))

def use_item(inventory: dict, item_id: str, player_status: dict, items: dict):
    # 1) そもそも持っている？
    if inventory.get(item_id, 0) <= 0:
        return False, "持っていない…"

    # 2) 定義がある？
    if item_id not in items:
        return False, f"未定義アイテム: {item_id}"

    info = items[item_id]
    heal = int(info.get("heal", 0))

    # 3) 回復する（最小仕様：healが0なら何もしない）
    if heal > 0:
        hp = int(player_status.get("hp", 1))
        max_hp = int(player_status.get("max_hp", hp))
        new_hp = clamp(hp + heal, 0, max_hp)
        player_status["hp"] = new_hp

    # 4) 所持数を減らす
    inventory[item_id] = inventory.get(item_id, 0) - 1
    if inventory[item_id] <= 0:
        inventory.pop(item_id, None)

    name = info.get("name", item_id)
    if heal > 0:
        return True, f"{name}を使った！ HPが回復した。"
    return True, f"{name}を使った！"
