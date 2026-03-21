# Day3：NPC と会話イベントの日（7人×3時間用シナリオ）

## 0. 今日のゴール（先生が最初に読む用）

3時間で、次を「クラス全体」として完成させます。

1. フィールド（マップ）を歩き回れる  
2. NPC（話しかけられるキャラ）が立っている  
3. NPC のとなりでキーを押すと、画面下に会話ウィンドウが出てセリフが表示される  

### 絶対ルール

- `main_day1.py` / `main_day2.py` は **書き換え禁止**
- 触るファイルは、このプリントに書いてある場所だけ
- 迷ったら先生かこのプリントに必ず戻る

---

## 1. 今日の7人の役割（先に割り当てる）

| No | 役割名           | 触るファイル                  | ざっくりやること                     |
|----|------------------|-------------------------------|--------------------------------------|
| A  | NPC 担当         | `entities_student.py`         | NPC クラスを作る                     |
| B  | 当たり判定担当   | `entities_student.py` or 新規 | プレイヤーとNPCの「となり判定」      |
| C  | 会話ウィンドウUI | `ui/message_window.py/.kv`    | 画面下のメッセージ窓を作る           |
| D  | セリフ担当       | `input/events_day3.json`      | 会話データ（セリフ集）を作る         |
| E  | 村マップ担当     | `maps/`                       | 村マップを1つ作る                     |
| F  | つなぎ込み担当   | `main_day3.py`                | A〜Eの成果をゲームに結線する         |
| G  | テスト&記録担当  | `docs/Day3_buglog.md`         | バグ探し＆修正メモを書く             |

> 先生へ：  
> それぞれに名前を書き込んで配ってください。  
> 例：A=太郎、B=花子、… のように。

---

## 2. 今日の時間割（板書用）

- 0:00〜0:15　役割説明・割り当て（このプリントを読む）
- 0:15〜1:10　**個人作業**（A〜E中心、F/Gはサポート）
- 1:10〜2:10　**結合タイム**（Fがハブ、全員で `main_day3.py` に接続）
- 2:10〜2:50　テスト & バグ直し（主にG主導）
- 2:50〜3:00　今日のまとめ・画面お披露目

---

## 3. 各役割の「やることチェックリスト」

### 3-1. A：NPC 担当

**目的**：プレイヤーとは別の「話しかけられるキャラ」を表すクラスを作る。

- 触るファイル：`entities_student.py`
- 触ってはいけないファイル：`main_day1.py`, `main_day2.py`

#### Aさんのチェックリスト

- [ ] `entities_student.py` を開けた
- [ ] ファイルの一番下に `class NPC:` を追加した
- [ ] NPC に「名前・座標・イベントID」の3つを持たせた
- [ ] エラーが出ずに import できる

#### サンプルコード（ほぼコピペOK）

```python
class NPC:
    def __init__(self, name, x, y, event_id):
        # name: NPCの名前（例: "村人A"）
        # x, y: マップ上のタイル座標
        # event_id: 会話イベントのID（例: "first_npc"）
        self.name = name
        self.x = x
        self.y = y
        self.event_id = event_id
```

> ✅ Aさんは「**NPCというデータの箱を作る人**」です。  
> 動かすのは B と F の仕事なので、無理に動かそうとしなくて大丈夫。

---

### 3-2. B：当たり判定 担当

**目的**：プレイヤーがNPCの「となり」にいるかどうかを調べる関数を作る。

- 触るファイル：`entities_student.py`（か、新しい `helpers_day3.py` など）
- 触ってはいけないファイル：`main_day1.py`, `main_day2.py`

#### Bさんのチェックリスト

- [ ] `is_adjacent(player, npc)` という関数を作った
- [ ] プレイヤーとNPCが横に1マス離れたとき True になる
- [ ] まったく別の場所だと False になる

#### サンプルコード

```python
def is_adjacent(player, npc):
    # プレイヤーがNPCの上下左右どこか1マス隣にいるかどうかを返す。
    dx = abs(player.x - npc.x)
    dy = abs(player.y - npc.y)
    return dx + dy == 1
```

> ✅ Bさんは「**しゃべるきっかけを判定する人**」です。  
> キー入力でこの関数を呼ぶのは F の仕事です。

---

### 3-3. C：会話ウィンドウ UI 担当

**目的**：画面下に黒い箱＋白文字でセリフを1行表示できるようにする。

- 触るファイル：`ui/message_window.py`, `ui/message_window.kv`
- 触ってはいけないファイル：`main_day1.py`, `main_day2.py`

#### Cさんのチェックリスト

- [ ] `MessageWindow` クラスが作れた
- [ ] `text` プロパティがあって、文字列を入れられる
- [ ] `show_message(["こんにちは"])` で `text` に最初の1行が入る

#### `ui/message_window.py` のひな型

```python
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty

class MessageWindow(BoxLayout):
    # 画面下部にメッセージを表示するシンプルなウィンドウ
    text = StringProperty("")

    def show_message(self, text_list):
        # セリフのリストを受け取り、最初の1行だけ表示する簡易版。
        if not text_list:
            self.text = ""
            return
        self.text = text_list[0]
```

#### `ui/message_window.kv` のひな型

```kv
<MessageWindow>:
    size_hint_y: 0.25
    pos_hint: {"x": 0, "y": 0}
    orientation: "vertical"
    padding: 8
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.7
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: root.text
        text_size: self.width - 16, None
        halign: "left"
        valign: "top"
```

> ✅ Cさんは「**しゃべる場所を作る人**」です。  
> 何をしゃべるかは D / F の仕事です。

---

### 3-4. D：セリフ担当

**目的**：コードの中に日本語をベタ書きしないで、JSONファイルにまとめる。

- 触るファイル：`input/events_day3.json`
- JSONが壊れるとみんなの画面が止まるので注意！

#### Dさんのチェックリスト

- [ ] `input/` フォルダに `events_day3.json` を作った
- [ ] `{ "first_npc": [ "〜", "〜" ] }` という形になっている
- [ ] `{` と `}`、`[` と `]`、カンマの位置が正しい

#### ひな型（上書きして使ってOK）

```json
{
  "first_npc": [
    "ようこそ、最初の村へ！",
    "ここでは、イベントと会話のしくみを試しているんだ。",
    "他のNPCにも話しかけてみてごらん。"
  ],
  "shop_girl": [
    "いらっしゃいませ！ …と言いたいところだけど、まだお店は準備中なの。",
    "Day4でバトルやステータスを作ったら、また来てね。"
  ]
}
```

> ✅ Dさんは「**何をしゃべるかを決める人**」です。  
> ファイルを読む処理は F が書きます。

---

### 3-5. E：村マップ担当

**目的**：NPCを配置するための村マップを1枚作る。

- 触るフォルダ：`maps/`
- 触ってはいけない：既存の `.map` を削除・上書きしないこと

#### Eさんのチェックリスト

- [ ] 既存のマップファイルを1つコピーして、`village01.map` などにリネームした
- [ ] プレイヤーのスタート地点を1つ決めた（例：5,5）
- [ ] NPCを置きたい座標を紙にメモして、Aさん/Fさんに渡した

> ✅ Eさんは「**世界の形を作る人**」です。  
> マップの読み込み処理そのものは既存関数をFさんが呼びます。

---

### 3-6. F：つなぎ込み担当（今日のハブ）

**目的**：A〜Eが作った部品を `main_day3.py` で全部つなぐ。

- 触るファイル：`main_day3.py`
- 触ってはいけないファイル：`main_day1.py`, `main_day2.py`（ここ大事）

#### Fさんのチェックリスト

- [ ] `main_day3.py` を新規作成した（または用意されたたたき台を開いた）
- [ ] `setup_game()` 関数の中で  
  - マップ読み込み  
  - プレイヤー生成  
  - NPCリスト生成  
  - イベント読み込み  
  - MessageWindow生成  
  を行っている
- [ ] `on_key_press("e")` で  
  - 近くのNPCを探す（Bさんの関数を呼ぶ）  
  - 見つかったら `open_talk_window(npc.event_id)` を呼ぶ  

#### ひな型（コメント付き）

```python
from typing import List

# 実際のプロジェクトに合わせて import を直してください
# from entities_student import Player, NPC
# from map_loader_kivy import load_map
# from ui.message_window import MessageWindow
# from events_loader import load_events
# from entities_student import is_adjacent

player = None
npcs: List[object] = []
events: dict = {}
message_window = None

def setup_game():
    global player, npcs, events, message_window

    # 1) マップ読み込み
    # game_map = load_map("maps/village01.map")

    # 2) プレイヤー生成（座標はEさんと相談）
    # player = Player(x=5, y=5)

    # 3) NPC生成（座標はEさんと相談、event_idはDさんと相談）
    # npcs = [
    #     NPC("村人A", 8, 5, "first_npc"),
    #     NPC("お店の子", 10, 7, "shop_girl"),
    # ]

    # 4) イベント読み込み
    # events = load_events()

    # 5) メッセージウィンドウの生成と画面への追加
    # message_window = MessageWindow()
    # root_layout.add_widget(message_window)

def open_talk_window(event_id: str) -> None:
    if event_id not in events:
        print(f"[WARN] 未登録 event_id: {event_id}")
        return
    lines = events[event_id]
    if message_window is not None:
        message_window.show_message(lines)

def on_key_press(key: str) -> None:
    if key in ("up", "down", "left", "right"):
        # ここは既存の移動ロジックを呼び出す
        # move_player(key)
        return

    if key == "e":
        for npc in npcs:
            if is_adjacent(player, npc):
                open_talk_window(npc.event_id)
                break
```

> ✅ Fさんは「**線を全部つなぐ人**」です。  
> import する場所が分からないときは、必ず先生かA〜Eに相談してから書き換えます。

---

### 3-7. G：テスト & 記録担当

**目的**：みんなの作品を実際に動かし、バグや調整点を文章に残す。

- 触るファイル：`docs/Day3_buglog.md`

#### Gさんのチェックリスト

- [ ] `python main_day3.py` などでDay3が起動するか確認した
- [ ] プレイヤーが動くことを確認した
- [ ] NPCのとなりで `E` を押すと会話ウィンドウが出ることを確認した
- [ ] バグを見つけたら、原因と直し方を `Day3_buglog.md` に1件ずつ書いた

#### バグログの書き方（サンプル）

```text
【2025-xx-xx Day3】

■バグ1：NPCに話しかけるとエラー
内容：
    KeyError: 'first_npc'
原因：
    events_day3.json のキーが "first_npc" ではなく "first_npc01" になっていた
対策：
    NPC生成時の event_id を "first_npc01" に直して解決
```

---

## 4. 全員共通のNGリスト

- `main_day1.py` / `main_day2.py` は開いてもいいが **保存しないこと**
- 他の人の担当ファイルを勝手に直さない（相談してから）
- 分からないエラーを「なかったこと」にしない  
  → Gさんと一緒にバグログに書いてから先生に相談する

---

## 5. 今日のまとめメモ欄（クラス用）

- 今日できたこと：

- 次にやりたいこと（Day4 への宿題案など）：
