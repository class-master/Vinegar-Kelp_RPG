# Day5：フィールドとバトルをつなげる日（7人×3時間用シナリオ）

## 0. 今日のゴール（先生が最初に読む用）

3時間で、次を「クラス全体」として完成させます。

1. フィールド（マップ）上を歩き回っていると、**敵シンボルに触れたときにバトルが始まる**  
2. バトル画面で「こうげき」すると、**プレイヤーと敵の HP が減り、勝ち／負けが決まる**  
3. バトルに勝つと敵シンボルが消え、**フィールドに戻って探索を続けられる**

### 絶対ルール

- `main_day1.py` / `main_day2.py` / `main_day3.py` / `main_day4.py` は **書き換え禁止**（読むのは OK）  
- Day5 でコードを書く場所は、基本的に `main_day5.py` と `docs/Day5/Day5_buglog.md` だけ  
- 7人それぞれの担当（A〜G）は、**自分の STEP に書かれている場所だけ** を編集する  
- 迷ったら先生かこのプリントに必ず戻る

---

## 1. 今日の役割分担（7人）

| 人 | 役割名                       | 触るファイル                    | やることのイメージ                                       |
|----|------------------------------|---------------------------------|----------------------------------------------------------|
| A  | 敵シンボル担当               | `main_day5.py`                  | フィールド上の「敵の位置とステータス」の定義            |
| B  | エンカウント判定担当         | `main_day5.py`                  | プレイヤーが敵シンボルに触れたかどうかの判定            |
| C  | ステータス担当               | `main_day5.py`                  | プレイヤー／敵の HP・こうげき力の管理                   |
| D  | バトルUI担当                 | `main_day5.py`                  | 画面下のバトルウィンドウの見た目（HP表示など）          |
| E  | メッセージ＆ログ担当         | `main_day5.py`                  | 「◯◯があらわれた！」「こうげき！」などの文章デザイン    |
| F  | つなぎ込み担当               | `main_day5.py`                  | フィールド ↔ バトルのモード切り替えと全体の動作確認     |
| G  | テスト＆バグログ記録担当     | `docs/Day5/Day5_buglog.md`      | バグ探し・再現手順の記録・改善アイデアメモ              |

> 先生へ：  
> Day5 では **1ファイル集中（`main_day5.py`）** にして、A〜F を「担当する STEP ごと」に分けています。  
> それぞれの STEP にはコメントとサンプルコードを多めに書いてあるので、コピペ OK で進めてもかまいません。

---

## 2. 今日の時間割（板書用）

- 0:00〜0:15　役割説明・割り当て（このプリントを読む）  
- 0:15〜1:10　**個人作業**（A〜E がそれぞれの STEP を進める。F/G は全体の把握）  
- 1:10〜2:10　**結合タイム**（F をハブに、全員で `main_day5.py` を 1本にまとめる）  
- 2:10〜2:40　**テストタイム**（G 中心でバグ出し。バトル開始〜終了の流れを確認）  
- 2:40〜3:00　ふりかえり（バグログ共有＆「次はどう発展させたいか」アイデア出し）

---

## 3. 各役割の「やることチェックリスト」

### 3-1. A：敵シンボル担当

**目的**：フィールド上に「ここに敵がいるよ！」という印を置く。

- 触る場所：`main_day5.py` の **`EnemySymbol` クラスと `DEFAULT_ENEMIES` リスト**  
- まずは先生から配られた `main_day5.py` を開いて、`STEP A` と書かれているところを探す

#### Aさんがやること

1. `EnemySymbol` クラスのコメントを読んで、**「何を覚えている箱なのか」** を理解する  
2. `DEFAULT_ENEMIES` リストに、**敵を1〜2体追加してみる**（名前・位置・HP・攻撃力）  
3. マップを歩いて、**敵シンボルが狙った場所に描画されているか** 確認する  

```python
class EnemySymbol:
    def __init__(self, name: str, tile_x: int, tile_y: int,
                 hp: int = 10, attack: int = 3):
        # name      : 画面左上などに表示する敵の名前（例 "スライム"）
        # tile_x/y  : マップ上のタイル座標（0,0 が左上）
        # hp/attack : バトルで使う初期ステータス
        self.name = name
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defeated = False  # True ならフィールドから消す

# Aさんが遊べる場所（例）：
DEFAULT_ENEMIES: List[EnemySymbol] = [
    EnemySymbol("スライム", 10, 5, hp=12, attack=3),
    EnemySymbol("コウモリ", 14, 6, hp=8, attack=4),
    # ここに自分のオリジナル敵を足しても OK！
]
```

> ✅ Aさんは「**敵というデータの箱を作る人**」です。  
> 敵を動かしたりダメージを与えたりするのは、C〜F の仕事なので、  
> まずは **名前・位置・HP・攻撃力** を決めるところに集中しましょう。

---

### 3-2. B：エンカウント判定担当

**目的**：プレイヤーが敵シンボルに触れた瞬間を見つけて、バトル開始の合図を出す。

- 触る場所：`main_day5.py` の **`find_touched_enemy` 関数**  
- Day2 の「矩形衝突」の復習になっています

#### Bさんがやること

1. `find_touched_enemy` 関数のコメントをじっくり読む  
2. 「重なっていない条件」の考え方を Day2 のノートと見比べる  
3. まだ自信がない場合は、**下のサンプルコードを一行ずつコメントアウトしながら動きを確かめる**

```python
def find_touched_enemy(player_rect, enemies: List[EnemySymbol]) -> Optional[EnemySymbol]:
    px, py, pw, ph = player_rect
    for enemy in enemies:
        if enemy.defeated:
            continue
        ex, ey = enemy.pos_px
        ew = eh = TILE_SIZE - 6  # プレイヤーと同じくらいの大きさとする

        # 「重なっていない条件」を 1 つでも満たしたら接触していない
        separated = (
            px + pw <= ex or  # プレイヤーが左側
            ex + ew <= px or  # プレイヤーが右側
            py + ph <= ey or  # プレイヤーが上側
            ey + eh <= py     # プレイヤーが下側
        )
        if not separated:
            return enemy
    return None
```

> ✅ Bさんは「**プレイヤーと敵がぶつかった瞬間を見つける人**」です。  
> うまく行くと、当たり判定が OK なときだけ `start_battle()` が呼ばれます。

---

### 3-3. C：ステータス担当

**目的**：プレイヤーと敵の HP やこうげき力を 1 か所にまとめ、ダメージ処理を分かりやすくする。

- 触る場所：`main_day5.py` の **`BattleStatus` クラス** と  
  `Game.__init__` 内の `self.player_status` / `self.enemy_status` の初期化部分

#### Cさんがやること

1. `BattleStatus` のコメントを読み、**「1人分のステータス」を表すこと** を理解する  
2. プレイヤーの初期ステータス（HP, こうげき力）を相談して決める  
3. `apply_damage()` を使って、バトル中に HP が減ることを確認する  

```python
class BattleStatus:
    def __init__(self, name: str, max_hp: int, attack: int):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack

    def is_dead(self) -> bool:
        return self.hp <= 0

    def apply_damage(self, amount: int) -> None:
        """ダメージ量 amount を受けて HP を減らす helper。"""
        self.hp = max(0, self.hp - amount)
```

> ✅ Cさんは「**HP を減らす係**」です。  
> ダメージ計算をきれいにしておくと、あとで **防御力やスキル** を足しやすくなります。

---

### 3-4. D：バトルUI担当

**目的**：画面下にバトル用ウィンドウを描き、プレイヤーと敵の HP を見やすく表示する。

- 触る場所：`main_day5.py` の **`draw_battle_panel()` メソッド**  
- すでに黒い半透明のパネルは出るようになっているので、  
  その中に **HP やメッセージをどう配置するか** を考えます

#### Dさんがやること

1. `draw_battle_panel()` 内のコメントを読み、**どこに何を描くか** を決める  
2. 最低でも「プレイヤーの HP」「敵の HP」を文字で表示する  
3. 余裕があれば、「こうげき」「にげる」などのコマンド風テキストを追加してみる  

```python
def draw_battle_panel(self):
    panel_h = self.height * 0.35
    panel_y = 0
    # パネル背景
    Color(0, 0, 0, 0.7)
    Rectangle(pos=(0, panel_y), size=(self.width, panel_h))

    # HP 表示（C さん）
    Color(1, 1, 1, 1)
    player_text = f"{self.player_status.name} HP: {self.player_status.hp}/{self.player_status.max_hp}"
    enemy_text = ""
    if self.enemy_status:
        enemy_text = f"{self.enemy_status.name} HP: {self.enemy_status.hp}/{self.enemy_status.max_hp}"

    # ここに Label を置いて文字を描画するのが D さんのチャレンジです！
```

> ✅ Dさんは「**画面の見た目を整える人**」です。  
> 戦っている感じが出るように、文字の配置や強調の仕方を工夫してみましょう。

---

### 3-5. E：メッセージ＆ログ担当

**目的**：「◯◯があらわれた！」「こうげき！」「◯◯をたおした！」など、  
バトル中のメッセージを考えて、ログとして残す。

- 触る場所：`main_day5.py` の  
  - `start_battle()` 内で最初に `self.battle_log` を作っている部分  
  - `player_attack()` / `enemy_attack()` 内の `self.battle_log.append(...)` 部分

#### Eさんがやること

1. デフォルトの文章を、自分たちの世界観に合わせて書き換える  
2. ダメージ量も一緒に表示するなど、**読んでいて分かりやすいログ** にする  
3. バトルの開始〜終了までの流れを文章だけ読んで追えるか、クラスで確認する  

```python
def start_battle(self, enemy: EnemySymbol):
    self.mode = "battle"
    self.current_enemy = enemy
    self.enemy_status = BattleStatus(enemy.name, enemy.max_hp, enemy.attack)
    self.battle_turn = "player"
    self.battle_log = [
        f"{enemy.name} があらわれた！",
        "スペースキーで『こうげき』できます。",
    ]
```

> ✅ Eさんは「**RPGの文章担当**」です。  
> ログが読みにくいとバトルの流れが分からなくなるので、  
> 短くてもいいので **状況が伝わる日本語** を意識してみてください。

---

### 3-6. F：つなぎ込み担当

**目的**：フィールドモードとバトルモードをつなげて、  
「歩く → 敵に当たる → 戦う → フィールドに戻る」の流れを完成させる。

- 触る場所：`main_day5.py` の
  - `update_field()` の最後のエンカウント判定部分  
  - `start_battle()` / `player_attack()` / `enemy_attack()` の中で  
    `self.mode` を切り替えている部分

#### Fさんがやること

1. フィールド更新の流れを図にしてみる  
   - 入力 → 移動 → エンカウント判定 → バトル開始  
2. バトルで敵を倒したときに `self.mode = "field"` になっているか確認する  
3. 「敵がいなくなったあと、もう一度同じ場所を踏んでもバトルが始まらない」ことをテストする  

> ✅ Fさんは「**ゲーム全体の流れを組み立てる人**」です。  
> A〜E が作った部品をどう組み合わせるかを意識して、  
> 何度もテストプレイしながらバグを見つけていきましょう。

---

### 3-7. G：テスト＆バグログ担当

**目的**：今日見つかったバグ・気づき・改善アイデアを、  
あとから Day6 以降でも使えるように記録する。

- 触る場所：`docs/Day5/Day5_buglog.md`  

#### Gさんのチェックリスト

- [ ] 「やった操作（例：右に3マス歩いて敵に当たる）」を書いた  
- [ ] 「何が起きてほしかったか」「実際には何が起きたか」を分けて書いた  
- [ ] 直し方のアイデアが思いついたら、それもメモしておいた  

> ✅ Gさんは「**未来の自分たちの助っ人**」です。  
> 今日きれいに記録しておくと、Day6 以降で機能を増やすときに大きな助けになります。

---

## 4. 全員共通のNGリスト

- Day1〜Day4 のファイルを **上書き保存しない**（Day5 用にコピーする場合は必ずファイル名を変える）  
- 他の人の担当部分を、相談なしに削除・書き換えしない  
- 分からないエラーを「なかったこと」にしてファイルを消さない  
  → Gさんと一緒に **バグログに残してから先生に相談する**

---

## 5. 今日のまとめメモ欄（クラス用）

- 今日できたこと：

- 次にやりたいこと（Day6 への発展案など）：

