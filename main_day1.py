# -*- coding: utf-8 -*-
"""
RPG Steel Master D — Day1（生徒用）Kivy

────────────────────────────────────────────────────────────────────
■ Day1の到達（ゴール）
  ✅ CSVタイルマップを読み込んでタイルを描画できる
  ✅ プレイヤーを移動できる（壁すり抜けOKで良い）
  ✅ カメラ（スクロール）でプレイヤーを追従できる

────────────────────────────────────────────────────────────────────
■ これまでに出たエラーと、今回の“全文版”での対策
  1) FileNotFoundError（assets/maps/... が見つからない）
     → map_loader_kivy.py 側で「このファイル基準」にパス解決する想定

  2) ImportError: load_tileset_regions が無い
     → map_loader_kivy.py 側で load_tileset_regions を提供する想定

  3) KeyError: 0
     → CSVの 0 は「空マス」扱いが多い
     → draw() で tid==0 は描画しない（continue）

  4) TypeError: cannot unpack non-iterable int object
     → on_key_down が渡す key が int の環境がある
     → キー入力は “必ず文字列キー名” に正規化して扱う

  5) TypeError: _on_key_up() takes ... but ... were given
     → SDL2 の on_key_up は (window, key, scancode) のように引数個数が揺れる
     → _on_key_up は *args で余りを吸収する

  6) AttributeError: 'Game' object has no attribute '_on_key_up'
     → 関数定義がクラス外に出る（インデント崩れ）or 二重定義混在
     → このファイルでは “Gameクラス内に各1つだけ” に統一
"""

from __future__ import annotations

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Translate
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty

# プロジェクト設定（config.py）
# 例：
#   WIDTH, HEIGHT     : 画面サイズ
#   TILE_SIZE         : 1タイルのピクセルサイズ
#   MAP_CSV           : CSVマップのパス（assets/maps/steel_map01.csv など）
#   PLAYER_SPEED      : プレイヤー移動速度
#   BG                : 背景色 (r,g,b,a)
from config import WIDTH, HEIGHT, TILE_SIZE, MAP_CSV, PLAYER_SPEED, BG

# マップ読み込み＆タイル切り出し（map_loader_kivy.py）
from map_loader_kivy import load_csv_as_tilemap, load_tileset_regions


class Game(Widget):
    """
    ゲーム本体（KivyのWidget）

    Day1の方針：
      - まず“動く最小構成”を作る
      - 当たり判定は後（壁すり抜けOK）
      - 最適化（画面内だけ描画）は後
      - 入力は「押されているキー集合」を見る方式で分かりやすく
    """

    # カメラ移動量（描画時にTranslateする）
    cam = ListProperty([0, 0])

    # プレイヤー位置（ワールド座標）
    px = NumericProperty(0)
    py = NumericProperty(0)

    # プレイヤーサイズ（タイル1枚分）
    pw = NumericProperty(TILE_SIZE)
    ph = NumericProperty(TILE_SIZE)

    def __init__(self, **kw):
        super().__init__(**kw)

        # 画面に乗るWidgetとしてのサイズ
        self.size = (WIDTH, HEIGHT)

        # -------------------------------------------------------------
        # 1) マップ読み込み（CSV → grid）
        # -------------------------------------------------------------
        self.grid, self.rows, self.cols = load_csv_as_tilemap(MAP_CSV)

        # -------------------------------------------------------------
        # 2) タイルセット読み込み（tile_id → Texture）
        # -------------------------------------------------------------
        # 注意：0=空マスの設計だと、tiles に 0 は入らないのが普通です
        self.tiles = load_tileset_regions()

        # -------------------------------------------------------------
        # 3) プレイヤー初期位置
        # -------------------------------------------------------------
        self.px = TILE_SIZE * 2
        self.py = TILE_SIZE * 2

        # -------------------------------------------------------------
        # 4) キーボード入力の初期化（重要：ここで bind する）
        # -------------------------------------------------------------
        self._setup_keyboard()

        # -------------------------------------------------------------
        # 5) HUD（説明用）
        # -------------------------------------------------------------
        self.hud = Label(
            text="WASD / Arrow: Move | Day1 | tid=0 is empty (skipped)",
            size_hint=(None, None),
            pos=(10, HEIGHT - 30),
        )
        self.add_widget(self.hud)

        # -------------------------------------------------------------
        # 6) 毎フレーム更新
        # -------------------------------------------------------------
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    # =============================================================
    # 入力処理（キーボード）
    # =============================================================
    def _setup_keyboard(self):
        """
        キーボード入力初期化（bind登録）

        目的：
          - __init__ を読みやすく保つ
          - bind の登録位置がブレないようにする
          - インデント崩れによる AttributeError を起こしにくくする
        """
        # 押されているキー名（例：'a', 'left'）を入れる集合
        self.keys_down = set()

        # bind は「イベントが起きたら呼ぶ関数を登録」するだけ
        # ここで self._on_key_down / self._on_key_up が存在していないと落ちます
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)

    def _normalize_key_name(self, key, codepoint="") -> str:
        """
        キー情報を「小文字のキー名」に正規化します。

        Kivy/SDL2 の環境差で、key/keycode が
          - int
          - (int, str)
        のどちらで来るかが揺れるため、ここで吸収します。

        戻り値：
          例）'a', 'd', 'left', 'right', 'up', 'down' など
        """

        # (番号, 名前) 形式なら “名前” を採用
        if isinstance(key, (tuple, list)) and len(key) >= 2:
            return str(key[1]).lower()

        # int 形式なら Window.keycode_to_string で文字列化
        try:
            name = Window.keycode_to_string(key)
        except Exception:
            name = ""

        if isinstance(name, str) and name:
            return name.lower()

        # 最後の保険：codepoint が1文字なら使う
        if isinstance(codepoint, str) and len(codepoint) == 1:
            return codepoint.lower()

        return ""

    def _on_key_down(self, _window, key, scancode, codepoint, modifiers):
        """
        キー押下イベント

        SDL2/Kivy の一般的なシグネチャ：
          on_key_down(window, key, scancode, codepoint, modifiers)

        ここでやること（最小）：
          - キー名を正規化して keys_down に追加
        """
        key_name = self._normalize_key_name(key, codepoint)
        if key_name:
            self.keys_down.add(key_name)
        return True

    def _on_key_up(self, _window, keycode, *args):
        """
        キー離しイベント

        ★重要：
          SDL2 では on_key_up が
            on_key_up(window, key, scancode)
          のように “余分な引数” を渡すことがあります。

          そこで *args を受け取って、引数個数差で落ちないようにします。

        ここでやること（最小）：
          - キー名を正規化して keys_down から除去
        """
        key_name = self._normalize_key_name(keycode, "")
        if key_name:
            # discard は「無くてもエラーにしない」ので安全
            self.keys_down.discard(key_name)
        return True

    # =============================================================
    # 毎フレーム更新
    # =============================================================
    def update(self, dt):
        """
        毎フレーム呼ばれる処理（dt秒ぶん進める）

        Day1は当たり判定なし：
          - 押されているキー集合から移動方向を決める
          - 位置更新
          - カメラ追従
          - 描画
        """
        dx = 0
        dy = 0

        # WASD
        if "a" in self.keys_down:
            dx -= 1
        if "d" in self.keys_down:
            dx += 1
        if "w" in self.keys_down:
            dy += 1
        if "s" in self.keys_down:
            dy -= 1

        # Arrow keys
        if "left" in self.keys_down:
            dx -= 1
        if "right" in self.keys_down:
            dx += 1
        if "up" in self.keys_down:
            dy += 1
        if "down" in self.keys_down:
            dy -= 1

        # 速度を掛けて位置更新
        speed = PLAYER_SPEED
        self.px += dx * speed * dt
        self.py += dy * speed * dt

        # カメラ追従：プレイヤーを画面中央に見せる
        self.cam[0] = -(self.px - WIDTH / 2)
        self.cam[1] = -(self.py - HEIGHT / 2)

        # 描画
        self.draw()

    # =============================================================
    # 描画
    # =============================================================
    def draw(self):
        """
        タイル＋プレイヤーを描画します。

        KeyError: 0 対策：
          - tid==0 は「空マス」 → 描画しない
        """
        ts = TILE_SIZE

        # 毎フレーム描き直す（Day1は分かりやすさ優先）
        self.canvas.clear()

        with self.canvas:
            # 背景
            Color(*BG)
            Rectangle(pos=(0, 0), size=(WIDTH, HEIGHT))

            # カメラ
            PushMatrix()
            Translate(self.cam[0], self.cam[1])

            # タイル描画
            for r in range(self.rows):
                for c in range(self.cols):
                    tid = self.grid[r][c]

                    # ✅ 0は空：描かない
                    if tid == 0:
                        continue

                    # ✅ 未知IDも安全にスキップ
                    if tid not in self.tiles:
                        continue

                    Rectangle(
                        texture=self.tiles[tid],
                        pos=(c * ts, r * ts),
                        size=(ts, ts),
                    )

            # プレイヤー（簡易：白い四角）
            Color(1, 1, 1, 1)
            Rectangle(pos=(self.px, self.py), size=(self.pw, self.ph))

            PopMatrix()


class Day1App(App):
    """
    アプリ本体。build() で Game を返します。
    """

    def build(self):
        Window.size = (WIDTH, HEIGHT)
        return Game()


if __name__ == "__main__":
    Day1App().run()
