# -*- coding: utf-8 -*-
"""
Day6：アイテム定義（生徒用）

ここは「アイテムの内容」をまとめる場所です。
- main_day6.py に日本語や数値をベタ書きしないで済むようにします。
- 辞書（dict）なので JSON より壊れにくく、学習にも向いています。

追加の例：
    "antidote": {"name": "どくけし", "heal": 0}
"""

# item_id -> 定義
#   name: 表示名
#   heal: 回復量（0なら回復なし）
ITEMS = {
    "potion": {"name": "ポーション", "heal": 20},
    "hi_potion": {"name": "ハイポーション", "heal": 50},
}
