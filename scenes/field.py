# -*- coding: utf-8 -*-
"""
scenes/field.py – フィールド（# [A][B][C][D]）

なぜ→ Day1 の核（移動/衝突/HUD）を練習するため。
前提→ Kivy, CSV マップ（0=床,1=壁）, タイルサイズ `config.TILE`
入出力→ 入力: キー/ 出力: 画面, HUD テキスト
副作用→ フレームごとに状態更新
例外→ CSV 読込失敗時は落とさず床扱い 等
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import csv
from pathlib import Path
from typing import List

from src import config
from src.ui.hud import DebugHUD

# --- [C] マップ読込 --------------------------------------------------------
def load_csv_map(path: Path) -> List[List[int]]:
    """STEP: csv → 2次元配列（int）に変換。"""
    grid = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for row in csv.reader(f):
                grid.append([int(v) for v in row])
    except Exception as e:
        # HINT: 読込に失敗したら 0 だけの 10x10 を返す
        grid = [[0]*10 for _ in range(10)]
        print("[WARN] map load failed:", e)
    return grid

class GameField(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (config.WIDTH, config.HEIGHT)

        # [C] マップ
        self.map_grid = load_csv_map(config.DEFAULT_MAP_CSV)
        self.map_w = len(self.map_grid[0])
        self.map_h = len(self.map_grid)

        # プレイヤー（中心座標）
        self.x = config.TILE * 2.5
        self.y = config.TILE * 2.5
        self.dir = "down"
        self.vx = 0.0
        self.vy = 0.0

        # キー
        self.keys = set()
        self._kb = None

        # HUD
        self.hud = DebugHUD()
        self.add_widget(self.hud)

        # 入力取得 & ループ
        Clock.schedule_once(self._bind_kb, 0)
        Clock.schedule_interval(self.update, 1/60)

    def _bind_kb(self, *_):
        self._kb = Window.request_keyboard(self._kb_closed, self)
        if self._kb:
            self._kb.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

    def _kb_closed(self, *_):
        if self._kb:
            self._kb.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
            self._kb = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key_id, s = keycode
        self.keys.add(s)
        if s.lower() == "h":
            self.hud.visible = not self.hud.visible
        return True

    def _on_key_up(self, keyboard, keycode):
        key_id, s = keycode
        self.keys.discard(s)
        return True

    # --- [A] 入力/移動 -----------------------------------------------------
    def get_input_vector(self):
        """STEP1: 矢印/WASD を見て (ix, iy) を返す。右=+1 左=-1 上=+1 下=-1。
        HINT: 同時押しは -1/0/+1 の合成。斜めのときは長さを正規化(任意)。
        """
        left  = ("left" in self.keys) or ("a" in self.keys)
        right = ("right" in self.keys) or ("d" in self.keys)
        up    = ("up" in self.keys) or ("w" in self.keys)
        down  = ("down" in self.keys) or ("s" in self.keys)

        ix = (1 if right else 0) - (1 if left else 0)
        iy = (1 if up else 0) - (1 if down else 0)
        return ix, iy

    def update(self, dt: float):
        # 入力 → 速度（px/sec）
        ix, iy = self.get_input_vector()
        self.vx = ix * config.SPEED
        self.vy = iy * config.SPEED

        # 表示用の向き
        if abs(self.vx) > abs(self.vy):
            self.dir = "right" if self.vx > 0 else ("left" if self.vx < 0 else self.dir)
        elif abs(self.vy) > 0:
            self.dir = "up" if self.vy > 0 else "down"

        # --- [B] 衝突付き移動（STEPで書き換え） ---------------------------
        # いったんは「画面端でクランプ」だけの簡易版（必ず動く安全策）
        # STEP: X→衝突判定→Y→衝突判定 に置き換えてください
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        half_w, half_h = config.PLAYER_HALF_W, config.PLAYER_HALF_H
        # 画面端でのクランプ（仮）
        new_x = max(half_w, min(new_x, config.WIDTH - half_w))
        new_y = max(half_h, min(new_y, config.HEIGHT - half_h))
        self.x, self.y = new_x, new_y

        # --- 描画 ---------------------------------------------------------
        self.canvas.clear()
        with self.canvas:
            # 背景
            Color(*config.COLOR_BG)
            Rectangle(pos=(0,0), size=self.size)

            # タイル
            for ty in range(self.map_h):
                for tx in range(self.map_w):
                    val = self.map_grid[ty][tx]
                    Color(* (config.COLOR_WALL if val == 1 else config.COLOR_FLOOR))
                    Rectangle(pos=(tx*config.TILE, ty*config.TILE), size=(config.TILE, config.TILE))

            # プレイヤー
            Color(*config.COLOR_PLAYER)
            Rectangle(
                pos=(self.x - config.PLAYER_HALF_W, self.y - config.PLAYER_HALF_H),
                size=(config.PLAYER_HALF_W*2, config.PLAYER_HALF_H*2)
            )

        # HUD
        tile_x = int(self.x // config.TILE)
        tile_y = int(self.y // config.TILE)
        fps = 1.0 / dt if dt > 0 else 0.0
        self.hud.set_info(dict(x=self.x, y=self.y, dir=self.dir, fps=fps, tile_x=tile_x, tile_y=tile_y))

    # HINT: 下記2つを作ればタイル衝突が実現できます
    def is_blocked(self, tx: int, ty: int) -> bool:
        """STEP: マップ外は壁扱い。1=壁,0=床。"""
        if tx < 0 or ty < 0 or tx >= self.map_w or ty >= self.map_h:
            return True
        return self.map_grid[ty][tx] == 1

    def move_with_collision(self, dx: float, dy: float):
        """STEP: 軸ごとに移動→四隅のタイルを調べ、壁ならその軸の移動を取り消す。
        1) new_x = self.x + dx / new_y = self.y + dy
        2) 四隅 (±half_w, ±half_h) を new_x/new_y に足してタイル座標へ
        3) 1つでも壁なら、その軸は self.x/self.y を元に戻す
        4) X 軸→Y 軸の順で呼び出すと安定
        """
        # TODO: 実装してみよう（今は未使用。update から呼び出すと完成）
        pass

class FieldScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(GameField())
