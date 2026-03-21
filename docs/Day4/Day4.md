# Day4：バトルとステータスの基礎（7人×3時間用シナリオ）

## 0. 今日のゴール（先生が最初に読む用）

3時間で、次を「クラス全体」として完成させます。

1. Day3 までと同じようにフィールドを歩き回れる  
2. 特定の敵と **1対1のバトル** ができる  
3. プレイヤーと敵に「HP」と「攻撃力（＋防御）」があり、
   - Aキー（Attack）で攻撃
   - 敵のHPが0になったら「勝利！」
   - プレイヤーのHPが0になったら「やられてしまった……」  
   と表示されてフィールドに戻る

### 絶対ルール

- `main_day1.py` / `main_day2.py` / `main_day3.py` は **書き換え禁止**
- 触るファイルは、このプリントに書いてある場所だけ
- 迷ったら先生かこのプリントに必ず戻る

---

## 1. 今日の7人の役割（先に割り当てる）

| No | 役割名                 | 触るファイル                        | ざっくりやること                               |
|----|------------------------|-------------------------------------|-----------------------------------------------|
| A  | ステータス設計担当     | `status_day4.py`                    | HP・攻撃・防御などの「ステータス構造」を作る   |
| B  | ダメージ計算担当       | `battle_engine.py`                  | ダメージ計算＆攻撃処理を作る                   |
| C  | バトルUI担当           | `ui/battle_window.py/.kv`           | HPバー＆メッセージを表示する画面を作る         |
| D  | 敵データ担当           | `input/enemies_day4.json`           | 敵の名前・HP・攻撃力などのデータを作る         |
| E  | エンカウント設計担当   | （コードは触らなくてもOK）         | どこで／どうやってバトルを始めるかを決める     |
| F  | つなぎ込み担当         | `main_day4.py`                      | フィールド ←→ バトルの切り替えを実装する       |
| G  | テスト & 記録担当      | `docs/Day4_buglog.md`               | バトルを実際に動かして、バグログを書く         |

> 先生へ：  
> それぞれに名前を書き込んで配ってください。  
> 例：A=太郎、B=花子、… のように。

---

## 2. 今日の時間割（板書用）

- 0:00〜0:15　役割説明・割り当て（このプリントを読む）
- 0:15〜1:10　**個人作業**（A〜D中心、F/Gは設計とサポート）
- 1:10〜2:10　**結合タイム**（Fがハブ、`main_day4.py` に全部つなぐ）
- 2:10〜2:50　テスト & バグ直し（G主導でログを残す）
- 2:50〜3:00　今日のまとめ・画面お披露目

---

## 3. 各役割の「やることチェックリスト」

### 3-1. A：ステータス設計担当（`status_day4.py`）

**目的**：プレイヤー／敵の HP や攻撃力などをひとまとめで扱えるクラスを作る。

#### Aさんのチェックリスト

- [ ] `status_day4.py` を新規作成した
- [ ] `Status` クラス（または同等のクラス）を定義した
- [ ] 名前・最大HP・現在HP・攻撃力・防御力を持たせた
- [ ] `is_dead()` / `take_damage()` メソッドを用意した

#### ひな型（ほぼコピペOK）

```python
# status_day4.py

class Status:
    """プレイヤーや敵のステータスを表すシンプルなクラス。"""

    def __init__(self, name, max_hp, attack, defense=0):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense

    def is_dead(self) -> bool:
        """HPが0以下なら倒れているとみなす。"""
        return self.hp <= 0

    def take_damage(self, amount: int) -> int:
        """ダメージを受けてHPを減らす（0未満にはならない）。"""
        if amount < 0:
            amount = 0
        self.hp = max(self.hp - amount, 0)
        return self.hp
```

> ✅ Aさんは「**HPや攻撃力の“入れ物”を作る人**」です。  
> ダメージ計算そのものは Bさんに任せます。

---

### 3-2. B：ダメージ計算担当（`battle_engine.py`）

**目的**：攻撃したときのダメージ量と、攻撃の流れを決める。

#### Bさんのチェックリスト

- [ ] `battle_engine.py` を新規作成した
- [ ] `calc_damage(attacker, defender)` 関数を書いた
- [ ] `player_attack(player, enemy)` / `enemy_attack(enemy, player)` を用意した
- [ ] 返り値として「与えたダメージ量」が返るようにした

#### ひな型

```python
# battle_engine.py

from status_day4 import Status

def calc_damage(attacker: Status, defender: Status, base_power: int = 5) -> int:
    """攻撃側と防御側からダメージ量を計算する簡単な式。"""
    raw = attacker.attack + base_power - defender.defense
    return max(raw, 1)  # 最低1ダメージは入るようにする

def player_attack(player: Status, enemy: Status) -> int:
    """プレイヤーから敵への攻撃。実際にHPを減らしてダメージ量を返す。"""
    dmg = calc_damage(player, enemy)
    enemy.take_damage(dmg)
    return dmg

def enemy_attack(enemy: Status, player: Status) -> int:
    """敵からプレイヤーへの攻撃。"""
    dmg = calc_damage(enemy, player)
    player.take_damage(dmg)
    return dmg
```

> ✅ Bさんは「**どれくらいHPが減るか」を決める人**です。  
> 画面にどう表示するかは C/F の仕事です。

---

### 3-3. C：バトルUI担当（`ui/battle_window.py/.kv`）

**目的**：バトル中に HP とメッセージを表示するウィンドウを作る。

#### Cさんのチェックリスト

- [ ] `ui/battle_window.py` / `ui/battle_window.kv` を作った
- [ ] プレイヤー／敵の名前と HP を表示できる
- [ ] メッセージ（「○○のこうげき！」など）を1行表示できる
- [ ] `update_status(player, enemy)` でHP表示を更新できる

#### `ui/battle_window.py` のひな型

```python
# ui/battle_window.py

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class BattleWindow(BoxLayout):
    """Day4用の簡易バトル画面。HPとメッセージだけを扱う。"""

    player_name = StringProperty("")
    player_hp = StringProperty("")
    enemy_name = StringProperty("")
    enemy_hp = StringProperty("")
    message = StringProperty("")

    def update_status(self, player_status, enemy_status):
        """Status インスタンスから名前とHPの表示を更新する。"""
        self.player_name = player_status.name
        self.player_hp = f"HP: {player_status.hp}/{player_status.max_hp}"
        self.enemy_name = enemy_status.name
        self.enemy_hp = f"HP: {enemy_status.hp}/{enemy_status.max_hp}"

    def show_message(self, text: str):
        self.message = text
```

#### `ui/battle_window.kv` のひな型

```kv
<BattleWindow>:
    orientation: "vertical"
    padding: 8
    spacing: 8
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.8
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: 0.3
        spacing: 8

        BoxLayout:
            orientation: "vertical"
            Label:
                text: root.player_name
            Label:
                text: root.player_hp

        BoxLayout:
            orientation: "vertical"
            Label:
                text: root.enemy_name
            Label:
                text: root.enemy_hp

    BoxLayout:
        size_hint_y: 0.7
        Label:
            text: root.message
            text_size: self.width - 16, None
            halign: "left"
            valign: "top"
```

> ✅ Cさんは「**バトルの見た目を作る人**」です。  
> いつ表示／非表示にするかは Fさんが制御します。

---

### 3-4. D：敵データ担当（`input/enemies_day4.json`）

**目的**：敵の名前・HP・攻撃力などを JSONファイルにまとめる。

#### Dさんのチェックリスト

- [ ] `input/enemies_day4.json` を作った
- [ ] `"slime"`, `"goblin"` などのIDをキーにした
- [ ] 各敵に `name`, `max_hp`, `attack`, `defense` などを持たせた

#### ひな型

```json
{
  "slime": {
    "name": "スライム",
    "max_hp": 15,
    "attack": 4,
    "defense": 0
  },
  "goblin": {
    "name": "ゴブリン",
    "max_hp": 25,
    "attack": 6,
    "defense": 1
  }
}
```

> ✅ Dさんは「**どんな敵が出てくるか** を決める人です」。  
> このデータを読み込んで使うのは Fさんの仕事です。

---

### 3-5. E：エンカウント設計担当（紙＋先生との相談）

**目的**：

- 「どのNPC/場所からバトルに入るのか」
- 「一度勝ったらその敵は消すかどうか」

などのルールを決める。

#### Eさんのチェックリスト

- [ ] 「どのNPCに話しかけたらバトルが始まるか」を決めて紙に書いた
- [ ] そのNPCに対応する敵ID（例: `"slime"`）を決めた
- [ ] 勝利後にどうするか（敵を消す／また戦える）を決めた
- [ ] 決めた内容を FさんとGさんに共有した

> ✅ Eさんは「**ゲームデザイン担当**」です。  
> コードを無理に書かなくてもOK。その代わり仕様をはっきりさせます。

---

### 3-6. F：つなぎ込み担当（`main_day4.py`）

**目的**：フィールドとバトルを切り替える「司令塔」を作る。

#### Fさんのチェックリスト

- [ ] `main_day4.py` を新規作成した
- [ ] `mode` 変数で `"field"` / `"battle"` を切り替えるようにした
- [ ] `start_battle(enemy_id)` 関数でバトルを開始できる
- [ ] A/B/C/D/E の成果を import して使っている
- [ ] バトル中に Aキーで攻撃 → 勝敗がついたらフィールドに戻る流れになっている

#### ひな型（コメント付き）

```python
# main_day4.py

from typing import Optional

# 実プロジェクトに合わせて import を書き換えてください
# from status_day4 import Status
# from battle_engine import player_attack, enemy_attack
# from ui.battle_window import BattleWindow
# from input_loader import load_enemy_status  # ← Day4用に作ってもOK

mode = "field"  # "field" または "battle"

player_status = None      # Status
enemy_status: Optional["Status"] = None
battle_window = None      # BattleWindow インスタンス

def setup_game():
    """Day4 用の初期化。フィールド側のセットアップ＋ステータス準備。"""
    global player_status, battle_window
    # ここで Day3 と同様にフィールドの準備を行う想定です。
    # 例: setup_field() などの関数を呼ぶ。

    # プレイヤーの初期ステータス（仮の値）
    # player_status = Status("ゆうしゃ", max_hp=30, attack=8, defense=2)

    # バトルウィンドウ作成（画面レイアウトに合わせて追加）
    # battle_window = BattleWindow()
    # root_layout.add_widget(battle_window)
    # battle_window.opacity = 0  # 最初は非表示

def start_battle(enemy_id: str):
    """Day4 のバトル開始処理。敵ステータスを用意し、UIをバトルモードにする。"""
    global mode, enemy_status

    # enemy_status = load_enemy_status(enemy_id)
    mode = "battle"

    # battle_window.opacity = 1
    # battle_window.update_status(player_status, enemy_status)
    # battle_window.show_message(f"{enemy_status.name} があらわれた！")

def end_battle(message: str):
    """バトル終了処理。メッセージを出してからフィールドに戻る想定。"""
    global mode, enemy_status
    mode = "field"
    enemy_status = None
    # battle_window.show_message(message)
    # battle_window.opacity = 0
    # ここで必要ならNPCを消すなどの処理を入れる

def handle_battle_key(key: str):
    """バトル中のキー入力を処理する。今は Aキーで攻撃だけ想定。"""
    if key.lower() != "a":
        return

    # 1) プレイヤーの攻撃
    # dmg = player_attack(player_status, enemy_status)
    # battle_window.update_status(player_status, enemy_status)
    # battle_window.show_message(f"{player_status.name} のこうげき！ {enemy_status.name} に {dmg} ダメージ！")

    # if enemy_status.is_dead():
    #     end_battle(f"{enemy_status.name} を たおした！")
    #     return

    # 2) 敵の反撃
    # dmg2 = enemy_attack(enemy_status, player_status)
    # battle_window.update_status(player_status, enemy_status)
    # battle_window.show_message(f"{enemy_status.name} のこうげき！ {player_status.name} は {dmg2} ダメージをうけた！")

    # if player_status.is_dead():
    #     end_battle("やられてしまった……")
    #     # プレイヤーのHPリセットなどはここで行う

def on_key_press(key: str):
    """全体のキー入力ハンドラ。フィールドモード/バトルモードで処理を分ける。"""
    if mode == "battle":
        handle_battle_key(key)
        return

    # mode == "field" のときは、今まで通りの移動などを行う
    if key in ("up", "down", "left", "right"):
        # move_player(key)
        return

    # 例えば Day3 の「NPCに話しかける」処理の一部から
    # start_battle("slime") を呼ぶとバトルに入れるイメージです。
```

> ✅ Fさんは「**ゲーム全体の流れをまとめる人**」です。  
> うまく動かないときは、A〜E/Gと一緒に原因を切り分けます。

---

### 3-7. G：テスト & 記録担当（`docs/Day4_buglog.md`）

**目的**：Day4 のバトル機能を実際に触って、バグや調整点を文章で残す。

#### Gさんのチェックリスト

- [ ] `python main_day4.py` などで Day4 を起動した
- [ ] フィールドを歩いて、決めた条件でバトルが始まることを確認した
- [ ] Aキーで攻撃 → 勝敗がついたらフィールドに戻ることを確認した
- [ ] 見つけたバグを `Day4_buglog.md` に1件ずつ書いた

#### バグログの書き方（サンプル）

```text
【2025-xx-xx Day4】

■バグ1：プレイヤーのHPがマイナスになる
内容：
    スライムの攻撃で HP が -3 になった
原因：
    take_damage() で 0 未満を切り捨てていなかった
対策：
    Status.take_damage() の中で max(self.hp - amount, 0) とする
```

---

## 4. 全員共通のNGリスト

- `main_day1.py` / `main_day2.py` / `main_day3.py` は開いてもいいが **保存しないこと**
- 他の人の担当ファイルを勝手に直さない（相談してから）
- 分からないエラーを「なかったこと」にしない  
  → Gさんと一緒にバグログに書いてから先生に相談する

---

## 5. 今日のまとめメモ欄（クラス用）

- 今日できたこと：

- 次にやりたいこと（Day5 への宿題案など）：
