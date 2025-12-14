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

        # ===== 講師用 模範解答（TODO: 走る/Shift） =========================
        # 【このTODOは何？】
        # - Shiftキーが押されている間だけ「移動速度を上げる」機能です。
        # - Day1では“当たり判定なし(すり抜けOK)”なので、速度を上げても実装が単純です。
        #
        # 【なぜ 303/304？】
        # - Kivyのキーコードは環境により差がありますが、一般に
        #   303=左Shift / 304=右Shift が多いです。
        # - どちらかが押されていれば「走る」と判断します。
        #
        # 【実装の形（最小でOK）】
        # - speed を倍率で上げるだけ。
        # - “押しっぱなし”は self.keys に入っているかどうかで表現できます。
        if (303 in self.keys) or (304 in self.keys):
            speed *= RUN_MULTIPLIER
        # ==================================================================

        # TODO: 慣性＋摩擦
        # self.vx = self.vx*(1-ACCEL) + ax*speed*ACCEL
        # self.vy = self.vy*(1-ACCEL) + ay*speed*ACCEL
        # self.vx *= FRICTION; self.vy *= FRICTION
        # self.vx = ax*speed; self.vy = ay*speed

        # ===== 講師用 模範解答（TODO: 慣性＋摩擦） =========================
        # 【このTODOは何？】
        # - “慣性” ＝ キー入力を変えても速度が急に切り替わらず、なめらかに変化すること。
        # - “摩擦” ＝ キー入力を離したときに、自然に減速して止まること。
        #
        # 【慣性の式（超定番）】
        #   v = v*(1-ACCEL) + v_target*ACCEL
        # - v_target は「入力が示す目標速度」（ax*speed, ay*speed）
        # - ACCEL は 0〜1 の範囲を想定：
        #   - 小さいほど“重い”（反応が遅い、慣性が強い）
        #   - 大きいほど“軽い”（反応が速い、慣性が弱い）
        #
        # 【摩擦の式（超定番）】
        #   v *= FRICTION
        # - FRICTION は 0〜1 を想定：
        #   - 0.8 なら早く止まる
        #   - 0.95 ならツルツル滑る
        #
        # 【実装順序（ここ大事）】
        # 1) まず慣性で v を目標速度へ寄せる
        # 2) その後に摩擦を掛ける（入力ゼロでも自然に減速する）
        #
        # ※ Day1は衝突なしなので、この vx/vy をそのまま座標に足してOKです。
        self.vx = self.vx*(1-ACCEL) + ax*speed*ACCEL
        self.vy = self.vy*(1-ACCEL) + ay*speed*ACCEL
        self.vx *= FRICTION; self.vy *= FRICTION
        # ==================================================================

        self.px += self.vx; self.py += self.vy

        # TODO: Clamp（マップ端）

        # ===== 講師用 模範解答（TODO: Clamp/マップ端で止める） =============
        # 【このTODOは何？】
        # - “Clamp” ＝ 値を範囲内に押し込むこと（はみ出させない）
        # - プレイヤーがマップの外へ出ないように、px/py を制限します。
        #
        # 【なぜ必要？】
        # - すり抜けOKでも、マップ外へ行くと“何も無い黒い世界”になりがち。
        # - Day1の学習では「画面の中で気持ちよく動ける」を優先したいので、
        #   端で止める（Clamp）が最も簡単で効果が高いです。
        #
        # 【範囲の作り方（ここがコツ）】
        # - マップのピクセル幅  = cols * TILE_SIZE
        # - マップのピクセル高さ = rows * TILE_SIZE
        # - プレイヤーは “左下座標(px,py)” なので、
        #   右端/上端を超えないように
        #     px <= map_w - player_w
        #     py <= map_h - player_h
        ts = TILE_SIZE
        map_w = self.cols * ts
        map_h = self.rows * ts
        player_w = ts - 6
        player_h = ts - 6

        # clamp(x, min, max) を手書き（Day1なので分かりやすさ優先）
        if self.px < 0:
            self.px = 0
        if self.py < 0:
            self.py = 0
        if self.px > map_w - player_w:
            self.px = map_w - player_w
        if self.py > map_h - player_h:
            self.py = map_h - player_h
        # ==================================================================

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
