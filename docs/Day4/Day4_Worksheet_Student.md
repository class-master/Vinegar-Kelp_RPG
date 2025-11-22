# Day4：バトルとステータスの日（7人×3時間用シナリオ）

## 0. 今日のゴール（先生が最初に読む用）

3時間で、次を「クラス全体」として完成させます。

1. プレイヤーと敵キャラに「HP / 攻撃力」が設定されている  
2. シンプルなバトル画面で「攻撃」コマンドが使える  
3. HP が 0 になったら「勝ち／負け」のメッセージが出る  

### 絶対ルール

- `main_day1.py` / `main_day2.py` / Day3 のフィールド部分は **書き換え禁止**
- 触るファイルは、このプリントに書いてある場所だけ
- 迷ったら先生かこのプリントに必ず戻る

---

## 1. 今日の7人の役割（先に割り当てる）

| No | 役割名                 | 触るファイル                           | ざっくりやること                           |
|----|------------------------|----------------------------------------|--------------------------------------------|
| A  | プレイヤーステータス   | `entities_student.py`                  | Player の HP/攻撃力/防御力 を持たせる      |
| B  | 敵キャラ担当           | `entities_student.py` or `core/enemy.py` | 敵クラスと敵パラメータを定義する         |
| C  | バトル画面UI           | `ui/battle_window.py/.kv`              | HPバーとメッセージ欄を作る                 |
| D  | ダメージ計算ロジック   | `core/battle_logic.py`                 | 1ターンの攻撃処理を書く                    |
| E  | エンカウント担当       | `scenes/field.py` など                 | フィールドからバトル画面へ切り替える起点を作る |
| F  | つなぎ込み担当         | `main_day4.py`                          | A〜E を一つの流れにまとめる                |
| G  | テスト&記録担当        | `docs/Day4_buglog.md`                  | 勝ち/負けのテストとバグログを書く          |

> 先生へ：  
> Day3 の NPC 会話とつながる形で、「この人に話しかけたらバトルが始まる」などにしてもOKです。

---

## 2. 今日の時間割（板書用）

- 0:00〜0:15　役割説明・割り当て（このプリントを読む）
- 0:15〜1:10　**個人作業**（A〜D中心、E/F/Gはサポート）
- 1:10〜2:10　**結合タイム**（Fがハブ、全員で `main_day4.py` に接続）
- 2:10〜2:40　**テストタイム**（Gが中心、勝ち/負けのパターンを試す）
- 2:40〜3:00　ふりかえり（バグログ共有＆次回の宿題相談）

---

## 3. 各役割の「やることチェックリスト」

### 3-1. A：プレイヤーステータス担当

**目的**：Player が HP や攻撃力などのパラメータを持つようにする。

- 触るファイル：`entities_student.py`
- 触ってはいけないファイル：`main_day1.py`, `main_day2.py`, Day3 のたたき台

#### Aさんのチェックリスト

- [ ] Player 用のクラスに `hp`, `max_hp`, `atk`, `defence` などを追加した
- [ ] 初期値（例：HP 30 / 攻撃 5 / 防御 2）を設定した
- [ ] エラーが出ずにゲームが起動する

#### サンプルコード（ほぼコピペOK）

```python
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Day4で追加するステータス
        self.max_hp = 30
        self.hp = 30
        self.atk = 5
        self.defence = 2
```

---

### 3-2. B：敵キャラ担当

**目的**：バトル用の敵キャラと、そのステータスを定義する。

- 触るファイル：`entities_student.py` または `core/enemy.py`

#### Bさんのチェックリスト

- [ ] `Enemy` クラス（名前 / HP / 攻撃力）を作った
- [ ] 「スライム」など、最低1体ぶんの初期データを作った
- [ ] printで中身を表示して値を確認した

#### サンプルコード

```python
class Enemy:
    def __init__(self, name, max_hp, atk):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
```

---

### 3-3. C：バトル画面 UI 担当

**目的**：画面に HP とメッセージを表示する簡単なバトルウィンドウを作る。

- 触るファイル：`ui/battle_window.py`, `ui/battle_window.kv`

#### Cさんのチェックリスト

- [ ] `BattleWindow` クラスを作った（`BoxLayout` を継承）
- [ ] プレイヤーと敵の HP を表示するラベルを2つ用意した
- [ ] メッセージを表示するためのラベルを1つ用意した

#### `ui/battle_window.py` のひな型

```python
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class BattleWindow(BoxLayout):
    player_hp_text = StringProperty("")
    enemy_hp_text = StringProperty("")
    message_text = StringProperty("")

    def update_status(self, player, enemy):
        self.player_hp_text = f"あなた HP: {player.hp}/{player.max_hp}"
        self.enemy_hp_text = f"{enemy.name} HP: {enemy.hp}/{enemy.max_hp}"
```

---

### 3-4. D：ダメージ計算ロジック担当

**目的**：1ターン分の「攻撃」処理を関数として切り出す。

- 触るファイル：`core/battle_logic.py`

#### Dさんのチェックリスト

- [ ] `attack(attacker, defender)` 関数を作った
- [ ] ダメージ = `max(1, attacker.atk - defender.defence)` のような式で計算した
- [ ] defender.hp が 0 を下回らないようにした

#### サンプルコード

```python
def attack(attacker, defender):
    raw = attacker.atk - getattr(defender, "defence", 0)
    dmg = max(1, raw)
    defender.hp = max(0, defender.hp - dmg)
    return dmg
```

---

### 3-5. E：エンカウント担当

**目的**：フィールドで何かをしたときに、バトルが始まるきっかけを作る。

- 触るファイル：`scenes/field.py` など（先生指定のファイル）

#### Eさんのチェックリスト

- [ ] 「特定のタイルを踏んだら」「特定のNPCに話しかけたら」など、条件を1つ決めた
- [ ] 条件を満たしたときに `start_battle()` 関数を呼ぶようにした
- [ ] その条件が何かをプリントでログに出して確認した

---

### 3-6. F：つなぎ込み担当（今日のハブ）

**目的**：A〜Eが作った部品を `main_day4.py` で全部つなぐ。

- 触るファイル：`main_day4.py`
- 触ってはいけないファイル：`main_day1.py`, `main_day2.py`, Day3 の既存ファイル

#### Fさんのチェックリスト

- [ ] `main_day3.py` を参考に `main_day4.py` を作った
- [ ] プレイヤー / 敵 / BattleWindow / battle_logic を import している
- [ ] キーボード or ボタンで「攻撃」コマンドを呼び出せる

---

### 3-7. G：テスト & 記録担当

**目的**：勝ちパターン / 負けパターン の両方を再現し、バグを文章に残す。

- 触るファイル：`docs/Day4_buglog.md`

#### Gさんのチェックリスト

- [ ] 「自分が勝つ」パターンを1つ書いた
- [ ] 「自分が負ける」パターンを1つ書いた
- [ ] 直したいバグや、今後やりたい改善点を3つ以上メモした

---

## 4. 全員共通のNGリスト

- `main_day1.py` / `main_day2.py` / Day3 のフィールド処理は保存しない
- 他の人の担当ファイルを勝手に直さない（相談してから）
- 分からないエラーを「なかったこと」にしない  
  → Gさんと一緒にバグログに書いてから先生に相談する

---

## 5. 今日のまとめメモ欄（クラス用）

- 今日できたこと：

- 次にやりたいこと（Day5 への宿題案など）：
