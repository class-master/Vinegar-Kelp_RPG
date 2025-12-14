# -*- coding: utf-8 -*-
"""
Day6（生徒用）：Kivy/KivyMD
到達：宝箱→入手→所持品→使用（回復）で、RPGの循環を作る

★このファイルは Day6 専用の「練習用メイン」です。
  - Day1〜Day5 のファイルには触らず、このファイルだけで遊んでOK。
  - 7人の役割ごとに「STEP A〜F」のコメントがあるので、
    自分の担当の STEP だけを集中して書きましょう。

操作：
  - 方向キー：移動
  - E：宝箱を開ける（となりで）
  - I：所持品ウィンドウの表示切替
  - 1：ポーションを使う（最小仕様：potion）
"""

from typing import List, Dict, Tuple, Optional

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Translate

from config import WIDTH, HEIGHT, TILE_SIZE, MAP_CSV, PLAYER_SPEED, BG
from map_loader_kivy import load_csv_as_tilemap, load_tileset_regions

from items_day6 import ITEMS
from ui.inventory_window import InventoryWindow
from systems.use_item import use_item

# ----------------------------------------------------------------------
# STEP A：宝箱データ（Aさん担当）
# ---------------------------------------------
class Chest:
    """宝箱（フィールド上の“開けられる物”）"""
    def __init__(self, tile_x: int, tile_y: int, item_id: str):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.item_id = item_id
        self.opened = False
    def open(self):
        if self.opened:
            return "宝箱はすでに開いています"
        self.opened = True
        return f"宝箱をあけた。中には{self.item_id}が入っていた"


    def pos_px(self) -> Tuple[int, int]:
        return self.tile_x * TILE_SIZE, self.tile_y * TILE_SIZE

# ★配置例：好きな座標に置いてOK（壁の上だと見えにくいので注意）
DEFAULT_CHESTS: List[Chest] = [
    Chest(8, 6, "potion"),
    Chest(12, 6, "hi_potion"),
]

# ----------------------------------------------------------------------
# STEP B：となり判定（Bさん担当）
# ---------------------------------------------
def is_adjacent_tile(px: int, py: int, cx: int, cy: int) -> bool:
    """上下左右1マスとなりならTrue。斜めはFalse。"""
    dx = abs(px - cx)
    dy = abs(py - cy)
    return dx + dy == 1

# ----------------------------------------------------------------------
# STEP C：所持品データ（Cさん担当の成果を使う側）
# ---------------------------------------------
def inventory_to_lines(inventory: Dict[str, int]) -> List[str]:
    """所持品辞書を、UI表示用の文字列リストにする。"""
    lines: List[str] = []
    
    ITEMS = {
        "potion": {"name": "ポーション", "heal": 20},
        "hi_potion": {"name": "ハイポーション", "heal": 50}
    }
    for item_id, count in sorted(inventory.items()):
        name = ITEMS.get(item_id, {}).get("name", item_id)
        lines.append(f"{name} x{count}")
    return lines

    ITEMS = {
        "potion": {"name": "ポーション", "heal": 20},
        "hi_potion": {"name": "ハイポーション", "heal": 50}
    }



# ----------------------------------------------------------------------
# Game本体
# ----------------------------------------------------------------------
class Game(Widget):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.size = (WIDTH, HEIGHT)

        # マップ読み込み（Day1と同じ資産を使う）
        self.grid, self.rows, self.cols = load_csv_as_tilemap(MAP_CSV)
        self.tiles = load_tileset_regions()

        # プレイヤー（タイル座標）
        self.px = 5
        self.py = 5

        # カメラ（ピクセル）
        self.cam_x = 0
        self.cam_y = 0

        # 宝箱
        self.chests: List[Chest] = [Chest(c.tile_x, c.tile_y, c.item_id) for c in DEFAULT_CHESTS]

        # 所持品 {item_id: count}
        self.inventory: Dict[str, int] = {}

        # ステータス（最小）
        self.status = {"hp": 30, "max_hp": 30}

        # 画面右上にデバッグラベル（ログ兼用）
        self.debug_label = Label(text="", halign="left", valign="top",
                                 size_hint=(None, None), size=(520, 160),
                                 pos=(16, HEIGHT - 160))
        self.add_widget(self.debug_label)

        # STEP D：所持品UI（Dさん担当）
        self.inv_window = InventoryWindow()
        self.add_widget(self.inv_window)

        # キーボード登録
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_key_down)

        Clock.schedule_interval(self.update, 1/60)

    def _on_keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None

    def _log(self, msg: str):
        # 1行ログ（簡易）
        self.debug_label.text = msg

    def _try_open_chest(self):
        """となりの宝箱を探して開ける（最小仕様：1個だけ）"""
        for chest in self.chests:
            if chest.opened:
                continue
            if is_adjacent_tile(self.px, self.py, chest.tile_x, chest.tile_y):
                chest.opened = True
                item_id = chest.item_id
                self.inventory[item_id] = self.inventory.get(item_id, 0) + 1
                name = ITEMS.get(item_id, {}).get("name", item_id)
                self._log(f"宝箱を開けた！ {name} を手に入れた。")
                self._refresh_inventory_ui()
                return
        self._log("近くに開けられる宝箱がない…")

    def _refresh_inventory_ui(self):
        self.inv_window.set_items(inventory_to_lines(self.inventory))

    def _use_potion_shortcut(self):
        """最小仕様：キー1で potion を使う"""
        ok, msg = use_item(self.inventory, "potion", self.status, ITEMS)
        self._refresh_inventory_ui()
        hp = self.status["hp"]
        mx = self.status["max_hp"]
        self._log(f"{msg}  HP:{hp}/{mx}")

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key = keycode[1]

        # 移動（壁すり抜けOKの最小仕様）
        if key in ("up", "w"):
            self.py -= 1
        elif key in ("down", "s"):
            self.py += 1
        elif key in ("left", "a"):
            self.px -= 1
        elif key in ("right", "d"):
            self.px += 1

        # 宝箱を開ける
        if key == "e":
            self._try_open_chest()

        # 所持品UIを開く
        if key == "i":
            self.inv_window.toggle()
            self._refresh_inventory_ui()

        # 使う（最小：1でポーション）
        if key == "1":
            self._use_potion_shortcut()

        # 画面外に出ないように雑にクランプ
        self.px = max(0, min(self.cols-1, self.px))
        self.py = max(0, min(self.rows-1, self.py))

        return True

    def update(self, dt):
        # カメラ追従（プレイヤーを中心にする）
        target_x = self.px * TILE_SIZE - WIDTH // 2 + TILE_SIZE // 2
        target_y = self.py * TILE_SIZE - HEIGHT // 2 + TILE_SIZE // 2
        self.cam_x = int(target_x)
        self.cam_y = int(target_y)
        self.canvas.clear()
        self.draw()

    def draw(self):
        ts = TILE_SIZE

        # 背景
        with self.canvas:
            Color(*BG)
            Rectangle(pos=(0, 0), size=(WIDTH, HEIGHT))

        # カメラ移動
        with self.canvas:
            PushMatrix()
            Translate(-self.cam_x, -self.cam_y)

            # マップ（CSVタイル）
            for r in range(self.rows):
                for c in range(self.cols):
                    tid = self.grid[r][c]
                    if tid < 0:
                        continue
                    if tid not in self.tiles:
                        continue
                    src = self.tiles[tid]
                    Rectangle(texture=src.texture, tex_coords=src.tex_coords,
                              pos=(c*ts, (self.rows-1-r)*ts), size=(ts, ts))

            # 宝箱（簡易：黄色い四角、開封済みは灰色）
            for chest in self.chests:
                x, y = chest.pos_px()
                if chest.opened:
                    Color(0.4, 0.4, 0.4, 1)
                else:
                    Color(1, 0.9, 0.2, 1)
                Rectangle(pos=(x+6, y+6), size=(ts-12, ts-12))

            # プレイヤー（青い四角）
            Color(0.2, 0.6, 1.0, 1)
            Rectangle(pos=(self.px*ts+4, self.py*ts+4), size=(ts-8, ts-8))

            PopMatrix()

class Day6App(App):
    def build(self):
        Window.size = (WIDTH, HEIGHT)
        return Game()

if __name__ == "__main__":
    Day6App().run()
