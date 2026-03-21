# -*- coding: utf-8 -*-
"""
目的: ダンジョン画面の下地。方位UI（コンパス）と現在地表示、キーボード入力の基本。
なぜ: 「どの方向を向いていて、どこにいるか」をUIで確かめられるようにするため。
前提: Compassウィジェット（ui/widgets/compass.py）が使える。
入出力: maps/dungeon_01.json（今回は読み込まず、テキストマップを生成）。
副作用: キーボードフォーカス要求（Window.request_keyboard）。
例外: 一部の環境ではフォーカスが取れずに入力が効かない場合あり。
"""
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from ui.widgets.compass import Compass

MAP_W, MAP_H = 10, 10  # ★ヒント: まずは10×10の箱庭でOK！

class DungeonScreen(MDScreen):
    # ★ヒント: プレイヤの現在地と向きをプロパティにしてUIと連動させる。
    x = NumericProperty(1)
    y = NumericProperty(1)
    facing = StringProperty("N")

    def on_pre_enter(self, *args):
        self.clear_widgets()

        # --- STEP1: 上部HUD（方位 + 現在地） ---
        root = MDBoxLayout(orientation="vertical", padding="12dp", spacing="8dp")
        hud = MDBoxLayout(orientation="horizontal", spacing="8dp", size_hint_y=None, height="48dp")
        self.compass = Compass(direction=self.facing)  # ★ヒント: directionが変わると表示が更新されるよ。
        self.status = MDLabel(text=self._status_text(), halign="left")
        hud.add_widget(self.compass)
        hud.add_widget(self.status)

        # --- STEP2: マップ（今回はテキストでOK） ---
        self.map_label = MDLabel(text=self._map_ascii(), halign="left")
        root.add_widget(hud)
        root.add_widget(self.map_label)
        self.add_widget(root)

        # --- STEP3: キーボード（WASD/矢印） ---
        # フォーカスが必要。ウィンドウを一度クリックしてから押すとうまくいくことが多いよ！
        self._keyboard = Window.request_keyboard(self._kb_closed, self, 'text')
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_key_down)

    # フォーカス解除時
    def _kb_closed(self):
        self._keyboard = None

    def on_leave(self, *args):
        if getattr(self, "_keyboard", None):
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None

    def _on_key_down(self, *args):
        # args: (keyboard, keycode, text, modifiers)
        _, keycode, text, modifiers = args
        key = keycode[1]

        # ★ヒント: このif分岐を読み解こう！自分で elif を書き足しても良い。
        dx = dy = 0
        if key in ("up", "w"):
            dy = -1; self.facing = "N"
        elif key in ("down", "s"):
            dy = 1; self.facing = "S"
        elif key in ("left", "a"):
            dx = -1; self.facing = "W"
        elif key in ("right", "d"):
            dx = 1; self.facing = "E"
        else:
            return False  # 他のキーは無視

        # ★ヒント: まずは範囲チェックだけ。壁の当たり判定は次回やってみよう。
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < MAP_W and 0 <= ny < MAP_H:
            self.x, self.y = nx, ny

        self._refresh_hud()
        return True

    # --- ヘルパ群 ---
    def _refresh_hud(self):
        self.status.text = self._status_text()
        self.compass.direction = self.facing
        self.map_label.text = self._map_ascii()

    def _status_text(self):
        return f"Pos: ({self.x},{self.y})  Facing: {self.facing}"

    def _map_ascii(self):
        # ★ヒント: '#'が壁、'.'が通路、'P'がプレイヤ。
        rows = []
        for j in range(MAP_H):
            row = []
            for i in range(MAP_W):
                if i == self.x and j == self.y:
                    row.append("P")
                elif i in (0, MAP_W-1) or j in (0, MAP_H-1):
                    row.append("#")
                else:
                    row.append(".")
            rows.append("".join(row))
        return "\\n".join(rows)
