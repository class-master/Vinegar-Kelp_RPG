# pyright: ignore
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path

from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

import random


class MapWidget(Widget):
    """
    MapWidget
    - 背景画像(view_path)を表示する
    - collision(0/1)で移動可否を判定する
    - start_cell が渡されたら、そのセルを開始位置にする
    - Town は右端だけ Field へ出る
    - Field では一定歩数で戦闘へ入る
    """

    def __init__(
        self,
        *,
        view_path: Path,
        collision: list[list[int]] | None,
        start_cell: tuple[int, int] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.player_tex = None
        player_path = Path(__file__).resolve().parent.parent.parent / "assets" / "images" / "brave_man.png"
        if player_path.exists():
            try:
                self.player_tex = CoreImage(str(player_path)).texture
            except Exception as e:
                print(f"[WARN] player image load failed: {player_path} ({e})")
                self.player_tex = None

        # 入力保持
        self.view_path = Path(view_path)
        self.collision = collision
        self.start_cell = start_cell

        # グリッドサイズ確定
        if self.collision:
            self.grid_h = len(self.collision)
            self.grid_w = len(self.collision[0])
        else:
            # フォールバック
            self.grid_w = 40
            self.grid_h = 32

        # 開始位置確定
        if start_cell is not None:
            self.px, self.py = start_cell
        else:
            self.px = max(0, min(self.grid_w - 1, self.grid_w // 2))
            self.py = max(0, min(self.grid_h - 1, self.grid_h // 2))

        # 歩数カウンタ
        self.steps = 0

        # 背景テクスチャ読み込み
        self.bg_tex = None
        if self.view_path.exists():
            try:
                self.bg_tex = CoreImage(str(self.view_path)).texture
            except Exception as e:
                print(f"[WARN] map image load failed: {self.view_path} ({e})")
                self.bg_tex = None
        else:
            print(f"[WARN] map image not found: {self.view_path}")

        # 描画
        with self.canvas:
            self._bg_color = Color(1, 1, 1, 1)
            self._bg = Rectangle(pos=self.pos, size=self.size, texture=self.bg_tex)

            self._player_color = Color(1, 1, 1, 1)
            self._player = Rectangle(pos=(0, 0), size=(0, 0), texture=self.player_tex)

        self.bind(pos=self._sync, size=self._sync)
        self._sync()

        # キー入力
        Window.bind(on_key_down=self._on_key)

    def on_parent(self, *args):
        """親から外れたらキー入力解除。"""
        if self.parent is None:
            try:
                Window.unbind(on_key_down=self._on_key)
            except Exception:
                pass

    def _cell_to_world(self, cx: int, cy: int) -> tuple[float, float]:
        """
        セル座標 -> Widget座標
        内部座標は左下原点。
        """
        cell_w = self.width / self.grid_w
        cell_h = self.height / self.grid_h

        x = self.x + cx * cell_w
        y = self.y + cy * cell_h
        return x, y

    def _sync(self, *args):
        """背景とプレイヤー位置を再描画。"""
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._bg.texture = self.bg_tex

        cell_w = self.width / self.grid_w
        cell_h = self.height / self.grid_h

        wx, wy = self._cell_to_world(self.px, self.py)
        pad_x = cell_w * 0.10
        pad_y = cell_h * 0.10

        self._player.pos = (wx + pad_x, wy + pad_y)
        self._player.size = (cell_w - pad_x * 2, cell_h - pad_y * 2)

        self._player.texture = self.player_tex


    def _can_walk(self, nx: int, ny: int) -> bool:
        """
        移動先が歩行可能か。

        CSVは上から下へ並ぶ。
        内部座標は下から上へ増える。
        なので参照時だけ row を変換する。
        """
        if not (0 <= nx < self.grid_w and 0 <= ny < self.grid_h):
            return False

        if not self.collision:
            return True

        csv_row = self.grid_h - 1 - ny
        return self.collision[csv_row][nx] == 0

    def _on_key(self, _w, key, scancode, codepoint, modifiers):
        # 今表示中の Screen でなければ反応しない
        if not self.parent or not self.parent.manager:
            return False
        if self.parent.manager.current != self.parent.name:
            return False

        dx = dy = 0

        # 矢印キー
        if key == 273:          # Up
            dy = 1
        elif key == 274:        # Down
            dy = -1
        elif key == 276:        # Left
            dx = -1
        elif key == 275:        # Right
            dx = 1
        else:
            # WASD
            if codepoint in ("w", "W"):
                dy = 1
            elif codepoint in ("s", "S"):
                dy = -1
            elif codepoint in ("a", "A"):
                dx = -1
            elif codepoint in ("d", "D"):
                dx = 1
            else:
                return False

        nx, ny = self.px + dx, self.py + dy

        if self._can_walk(nx, ny):
            self.px, self.py = nx, ny
            self._sync()
            self.steps += 1

            screen_name = getattr(self.parent, "name", "")

            # Town は右端だけ Field へ
            if screen_name == "town":
                if self.px == self.grid_w - 1:
                    if self.parent and self.parent.manager:
                        self.parent.manager.current = "field"
                        
                        if hasattr(self.parent.manager, "play_screen_bgm"):
                            self.parent.manager.play_screen_bgm("field")

                    return True

            # Field は左端で Town へ戻る
            if screen_name == "field":
                if self.px == 0:
                    if self.parent and self.parent.manager:
                        self.parent.manager.current = "town"
                        if hasattr(self.parent.manager, "play_screen_bgm"):
                            self.parent.manager.play_screen_bgm("town")                       
                    return True

                # Fieldだけ一定歩数で戦闘
                if self.steps >= 10:
                    self.steps = 0
                    if self.parent and self.parent.manager:
                        sc = self.parent.manager
                        player = sc.get_player_status()
                        enemy_id = random.choice(["slime", "knight", "goblin", "zoma"])
                        enemy, enemy_info = sc.load_enemy_status(enemy_id)
                        sc.start_battle(enemy=enemy, player=player, enemy_info=enemy_info)
                    return True

        return True