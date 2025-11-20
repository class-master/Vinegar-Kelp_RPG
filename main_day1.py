# -*- coding: utf-8 -*-
"""
Day1（生徒用）：Kivy/KivyMD
到達：タイル描画＋カメラ追従＋移動（壁すり抜けOK）
TODO：Shift走る／慣性／摩擦／Clamp（いずれか実装）
"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Translate
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty
from config import WIDTH, HEIGHT, TILE_SIZE, MAP_CSV, PLAYER_SPEED, RUN_MULTIPLIER, ACCEL, FRICTION, BG
from map_loader_kivy import load_csv_as_tilemap, load_tileset_regions

class Game(Widget):
    cam = ListProperty([0,0])
    def __init__(self, **kw):
        super().__init__(**kw)
        self.size = (WIDTH, HEIGHT)
        self.grid, self.rows, self.cols = load_csv_as_tilemap(MAP_CSV)
        self.tiles = load_tileset_regions()
        self.px = TILE_SIZE*2; self.py = TILE_SIZE*2
        self.vx = 0; self.vy = 0
        self.keys=set()
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
        self.hud = Label(text="矢印/WASDで移動 — TODO: 走る/慣性/摩擦/Clamp", pos=(12, HEIGHT-28))
        self.add_widget(self.hud)
        Clock.schedule_interval(self.update, 1/60)

    def _on_key_down(self, win, key, scancode, codepoint, modifiers):
        self.keys.add(key); return True
    def _on_key_up(self, win, key, *args):
        self.keys.discard(key); return True

    def update(self, dt):
        # 入力ベクトル
        import math
        left=276; right=275; up=273; down=274
        ax = (1 if right in self.keys else 0) - (1 if left in self.keys else 0)
        ay = (1 if down in self.keys else 0) - (1 if up in self.keys else 0)
        # TODO: 走る（Shift）
        speed = PLAYER_SPEED
        # if 304 in self.keys or 303 in self.keys:  # 左右Shift
        #     speed *= RUN_MULTIPLIER
        # TODO: 慣性＋摩擦
        # self.vx = self.vx*(1-ACCEL) + ax*speed*ACCEL
        # self.vy = self.vy*(1-ACCEL) + ay*speed*ACCEL
        # self.vx *= FRICTION; self.vy *= FRICTION
        self.vx = ax*speed; self.vy = ay*speed

        self.px += self.vx; self.py += self.vy
        # TODO: Clamp（マップ端）

        # カメラ追従
        self.cam[0] = max(0, self.px - self.width/2)
        self.cam[1] = max(0, self.py - self.height/2)

        self.draw()

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(*BG); Rectangle(pos=self.pos, size=self.size)
            PushMatrix(); Translate(-self.cam[0], -self.cam[1], 0)
            # タイル描画（小規模なので全面描画）
            ts=TILE_SIZE
            for r,row in enumerate(self.grid):
                for c,tid in enumerate(row):
                    if 0 <= tid < len(self.tiles):
                        Rectangle(texture=self.tiles[tid], pos=(c*ts, r*ts), size=(ts,ts))
            # プレイヤ
            Color(0.35,0.67,1.0,1)
            Rectangle(pos=(self.px, self.py), size=(ts-6, ts-6))
            PopMatrix()

class Day1App(App):
    def build(self):
        return Game()

if __name__ == "__main__":
    Day1App().run()
