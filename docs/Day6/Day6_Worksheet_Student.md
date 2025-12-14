# Day6：アイテムでRPGが回り始める日（7人×3時間用シナリオ）

## 0. 今日のゴール（先生が最初に読む用）

3時間で、次を「クラス全体」として完成させます。

1. フィールド上に **宝箱（Chest）** が置かれている  
2. 宝箱のとなりでキーを押すと **アイテムを獲得**できる  
3. 獲得したアイテムを **持ち物（Inventory）から使える**（回復アイテムでOK）

### 絶対ルール

- `main_day1.py` 〜 `main_day5.py` は **書き換え禁止**
- 触るファイルは、このプリントに書いてある場所だけ
- 迷ったら先生かこのプリントに必ず戻る

---

## 1. 今日の7人の役割（先に割り当てる）

| No | 役割名 | 触るファイル | ざっくりやること |
|----|--------|--------------|------------------|
| A  | 宝箱担当 | `main_day6.py` | 宝箱データ（Chest）と配置 |
| B  | 判定担当 | `main_day6.py` | 「となり判定」＋開ける判定 |
| C  | アイテム担当 | `items_day6.py` | アイテム定義（辞書） |
| D  | 所持品UI担当 | `ui/inventory_window.py` | 画面に所持品表示（簡易でOK） |
| E  | 使用処理担当 | `systems/use_item.py` | 使うと回復＆減る |
| F  | つなぎ込み担当 | `main_day6.py` | A〜Eを接続して動線完成 |
| G  | テスト&記録担当 | `docs/Day6/Day6_buglog.md` | バグ記録と再現手順 |

> 先生へ：  
> それぞれに名前を書き込んで配ってください。  
> 例：A=太郎、B=花子、… のように。

---

## 2. 今日の時間割（板書用）

- 0:00〜0:15　役割説明・割り当て（このプリントを読む）
- 0:15〜1:10　**個人作業**（A〜E中心、F/Gはサポート）
- 1:10〜2:10　**結合タイム**（Fがハブ、全員で `main_day6.py` に接続）
- 2:10〜2:50　テスト & バグ直し（主にG主導）
- 2:50〜3:00　今日のまとめ・画面お披露目

---

## 3. 各役割の「やることチェックリスト」

### 3-1. A：宝箱担当

**目的**：フィールド上に「開けられる宝箱」を表すデータを作る。

- 触るファイル：`main_day6.py`
- 触ってはいけない：`main_day1.py`〜`main_day5.py`

#### Aさんのチェックリスト

- [ ] `main_day6.py` を開けた
- [ ] `class Chest:` を追加した
- [ ] Chest に「座標・中身（item_id）・開封済みフラグ」を持たせた
- [ ] チェストが 1 個以上 `DEFAULT_CHESTS` に入っている

#### サンプルコード（ほぼコピペOK）

```python
class Chest:
    def __init__(self, tile_x: int, tile_y: int, item_id: str):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.item_id = item_id
        self.opened = False
```

> ✅ Aさんは「**宝箱という“箱”を作る人**」です。  
> 開ける判定やUIは他の担当なので、Aだけで完璧に動かさなくてOK。

---

### 3-2. B：判定担当（となり判定＋開ける判定）

**目的**：プレイヤーが宝箱の「となり」にいるかどうかを調べて、開けられるようにする。

- 触るファイル：`main_day6.py`

#### Bさんのチェックリスト

- [ ] `is_adjacent_tile(px, py, cx, cy)` を作った
- [ ] 上下左右1マスとなりで True
- [ ] 斜めは False

#### サンプルコード

```python
def is_adjacent_tile(px, py, cx, cy) -> bool:
    dx = abs(px - cx)
    dy = abs(py - cy)
    return dx + dy == 1
```

> ✅ Bさんは「**開けられる条件を作る人**」です。  
> 何がもらえるかはC、持ち物に入れるのはFの仕事です。

---

### 3-3. C：アイテム担当（定義ファイル）

**目的**：アイテムの情報を「コード内にベタ書き」せず、辞書にまとめる。

- 触るファイル：`items_day6.py`
- JSONでも良いが、今日は辞書でOK（壊れにくい）

#### Cさんのチェックリスト

- [ ] `ITEMS` 辞書がある
- [ ] `"potion"` が定義されている
- [ ] `name` と `heal` を持つ

#### ひな型（上書きして使ってOK）

```python
ITEMS = {
    "potion": {"name": "ポーション", "heal": 20},
    "hi_potion": {"name": "ハイポーション", "heal": 50},
}
```

---

### 3-4. D：所持品UI担当

**目的**：所持品を画面に表示する（最小実装でOK）。

- 触るファイル：`ui/inventory_window.py`

#### Dさんのチェックリスト

- [ ] `InventoryWindow` を作った
- [ ] `set_items(list_of_text)` で表示が更新される
- [ ] 表示/非表示を切り替えられる（show/hide）

#### ひな型

```python
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class InventoryWindow(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (320, 200)
        self.pos = (16, 16)
        self.label = Label(text="(empty)")
        self.add_widget(self.label)
        self.visible = False
        self.opacity = 0
        self.disabled = True

    def set_items(self, lines):
        self.label.text = "\n".join(lines) if lines else "(empty)"

    def show(self):
        self.visible = True
        self.opacity = 1
        self.disabled = False

    def hide(self):
        self.visible = False
        self.opacity = 0
        self.disabled = True
```

---

### 3-5. E：使用処理担当（回復＆減る）

**目的**：アイテムを使ったときに HP を回復し、所持数を減らす。

- 触るファイル：`systems/use_item.py`

#### Eさんのチェックリスト

- [ ] `use_item(inventory, item_id, player_status)` を作った
- [ ] `heal` があるアイテムを使うと HP が増える
- [ ] 所持数が 1 減る（0なら使えない）

---

### 3-6. F：つなぎ込み担当（今日のハブ）

**目的**：A〜Eが作った部品を `main_day6.py` で全部つなぐ。

- 触るファイル：`main_day6.py`

#### Fさんのチェックリスト

- [ ] `DEFAULT_CHESTS` が画面に表示される
- [ ] 宝箱のとなりで `E` キー → アイテム獲得
- [ ] `I` キー → 所持品ウィンドウ表示
- [ ] `1` キー → ポーションを使う（回復して減る）

> ✅ Fさんは「**線を全部つなぐ人**」です。  
> つながらない時は、必ず「どこまで動くか」をGと一緒に切り分けます。

---

### 3-7. G：テスト & 記録担当

- 触るファイル：`docs/Day6/Day6_buglog.md`

#### Gさんのチェックリスト

- [ ] `python main_day6.py` で起動できる
- [ ] 移動できる
- [ ] 宝箱を開けられる
- [ ] アイテムが表示される
- [ ] 回復できる

#### バグログの書き方（サンプル）

```text
【2025-xx-xx Day6】

■バグ1：宝箱のとなりでEを押しても取れない
内容：
    反応なし
原因：
    is_adjacent_tile の dx+dy が 1 ではなく 0 になっていた
対策：
    dx + dy == 1 に修正して解決
```

---

## 4. 全員共通のNGリスト

- `main_day1.py`〜`main_day5.py` は開いてもいいが **保存しないこと**
- 他の人の担当ファイルを勝手に直さない（相談してから）
- 分からないエラーを「なかったこと」にしない  
  → Gさんと一緒にバグログに書いてから先生に相談する

---

## 5. 今日のまとめメモ欄（クラス用）

- 今日できたこと：

- 次にやりたいこと（Day7 への宿題案など）：
