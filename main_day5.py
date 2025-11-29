# -*- coding: utf-8 -*-
"""
Day5（生徒用）：Kivy/KivyMD
到達：フィールドとバトルをつなげる（シンボルエンカウント）
発展：複数の敵、経験値・レベルアップ

★このファイルは Day5 専用の「練習用メイン」です。
  - Day1〜Day4 のファイルには触らず、このファイルだけで遊んでOK。
  - 7人の役割ごとに「STEP A〜F」のコメントがあるので、
    自分の担当の STEP だけを集中して書きましょう。
"""
from typing import List, Dict, Optional

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Translate
from kivy.uix.label import Label
from kivy.properties import ListProperty, StringProperty

from config import WIDTH, HEIGHT, TILE_SIZE, MAP_CSV, PLAYER_SPEED, BG
from map_loader_kivy import load_csv_as_tilemap, load_tileset_regions


# ----------------------------------------------------------------------
# STEP A：敵シンボルのデータ定義（Aさん担当）
# ----------------------------------------------------------------------
class EnemySymbol:
    """
    なぜ：フィールド上に「ここに敵がいるよ」という情報を置くため。
    前提：タイルマップの 1 マス = TILE_SIZE ピクセル。
    入出力：フィールド描画・当たり判定で参照されるだけ。
    副作用：なし（ただのデータの箱）。
    例外：特になし。
    """

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

    @property
    def pos_px(self):
        """この敵シンボルの左上ピクセル座標を返す helper。"""
        return self.tile_x * TILE_SIZE, self.tile_y * TILE_SIZE


# Day5 では、シンプルに 2 体だけあらかじめ配置しておく。
# ★位置は E さんがマップを見て決めても OK。
DEFAULT_ENEMIES: List[EnemySymbol] = [
    EnemySymbol("スライム", 10, 5, hp=12, attack=3),
    EnemySymbol("コウモリ", 14, 6, hp=8, attack=4),
]


# ----------------------------------------------------------------------
# STEP B：エンカウント判定（Bさん担当）
# ----------------------------------------------------------------------
def find_touched_enemy(player_rect, enemies: List[EnemySymbol]) -> Optional[EnemySymbol]:
    """
    なぜ：プレイヤーが敵シンボルの上に乗ったら、バトルを開始したいから。
    前提：player_rect は (x, y, w, h) の 4 つ組。
    入出力：接触している EnemySymbol を 1 体返す。いなければ None。
    副作用：なし（フラグをいじらない）。
    例外：特になし。

    ★Day2 の「矩形衝突」をシンプルに書き直したバージョンです。
      下のコードはほぼコピペで OK ですが、コメントを読みながら
      自分で書いてみても良いチャレンジです。
    """
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


# ----------------------------------------------------------------------
# STEP C：プレイヤー＆敵のステータス管理（Cさん担当）
# ----------------------------------------------------------------------
class BattleStatus:
    """
    なぜ：バトル中に使う「HP / 攻撃力 / 名前」などを 1 か所にまとめるため。
    前提：プレイヤーと敵で同じ型を使う。
    入出力：Game クラスから読み書きされる。
    副作用：ダメージを受けると hp が減る。
    例外：hp が 0 未満にならないように max() で守る。
    """

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


# ----------------------------------------------------------------------
# STEP D/E/F：ゲーム本体（つなぎ込み担当 F さん＋UI D さん＋メッセージ E さん）
# ----------------------------------------------------------------------
class Game(Widget):
    # Kivy 側からも参照しやすいように、いくつかの情報は Property にしておく
    debug_lines = ListProperty([])
    battle_log = ListProperty([])
    mode = StringProperty("field")  # "field" または "battle"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (WIDTH, HEIGHT)

        # --- マップ読み込み（Day1 の復習） --------------------------------
        self.grid, self.rows, self.cols = load_csv_as_tilemap(MAP_CSV)
        self.tiles = load_tileset_regions()

        # プレイヤー矩形（左上 px,py と幅高さ）
        self.px = TILE_SIZE * 3
        self.py = TILE_SIZE * 4
        self.w = TILE_SIZE - 6
        self.h = TILE_SIZE - 6

        # カメラ位置（左上）
        self.cam = [0.0, 0.0]

        # 移動用
        self.vx = 0.0
        self.vy = 0.0
        self.keys = set()

        # 敵シンボル（Aさんの EnemySymbol を利用）
        self.enemies: List[EnemySymbol] = [EnemySymbol(e.name, e.tile_x, e.tile_y, e.max_hp, e.attack)
                                           for e in DEFAULT_ENEMIES]

        # バトル用ステータス（Cさん担当）
        self.player_status = BattleStatus("主人公", max_hp=20, attack=5)
        self.enemy_status: Optional[BattleStatus] = None

        # どの敵と戦っているか
        self.current_enemy: Optional[EnemySymbol] = None

        # バトルのターン管理
        self.battle_turn = "player"  # "player" or "enemy"

        # 画面右上に簡単なデバッグ文字を出すラベル
        self.debug_label = Label(text="", halign="left", valign="top",
                                 size_hint=(None, None), size=(400, 150),
                                 pos=(16, HEIGHT - 150))
        self.add_widget(self.debug_label)

        # キーボード登録
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self._on_key_down,
                                on_key_up=self._on_key_up)

        # メインループ
        Clock.schedule_interval(self.update, 1/60)

    # ------------------------------------------------------------------
    # 入力処理
    # ------------------------------------------------------------------
    def _on_keyboard_closed(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down,
                                  on_key_up=self._on_key_up)
            self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key_id, s = keycode
        self.keys.add(s)

        # H キーでデバッグ表示の ON/OFF
        if s.lower() == "h":
            if self.debug_label.opacity > 0:
                self.debug_label.opacity = 0
            else:
                self.debug_label.opacity = 1
        return True

    def _on_key_up(self, keyboard, keycode):
        key_id, s = keycode
        if s in self.keys:
            self.keys.remove(s)
        return True

    # ------------------------------------------------------------------
    # 衝突ヘルパ（Day2 の復習） – 壁タイルは 1 を想定
    # ------------------------------------------------------------------
    def rect_collides_with_walls(self, nx: float, ny: float) -> bool:
        """
        プレイヤー矩形を (nx,ny) に動かしたとき、壁タイルとぶつかるかどうかを調べる。
        """
        ts = TILE_SIZE
        w, h = self.w, self.h

        left = int(nx // ts)
        right = int((nx + w - 1) // ts)
        top = int(ny // ts)
        bottom = int((ny + h - 1) // ts)

        solid_id = 1  # ★マップの「壁タイルID」に合わせて先生が調整

        for r in range(top, bottom + 1):
            if r < 0 or r >= self.rows:
                continue
            for c in range(left, right + 1):
                if c < 0 or c >= self.cols:
                    continue
                if self.grid[r][c] == solid_id:
                    return True
        return False

    # ------------------------------------------------------------------
    # メインループ
    # ------------------------------------------------------------------
    def update(self, dt):
        if self.mode == "field":
            self.update_field(dt)
        elif self.mode == "battle":
            self.update_battle(dt)
        self.draw()
        self.update_debug_text()

    # ------------------------------------------------------------------
    # フィールド更新（移動＋エンカウント判定） – 主に A/B/F さん担当
    # ------------------------------------------------------------------
    def update_field(self, dt):
        # --- 入力ベクトル（Day1 の復習） ----------------------------------
        left = 276; right = 275; up = 273; down = 274
        ax = (1 if right in self.keys else 0) - (1 if left in self.keys else 0)
        ay = (1 if down in self.keys else 0) - (1 if up in self.keys else 0)

        speed = PLAYER_SPEED
        self.vx = ax * speed
        self.vy = ay * speed

        # --- 衝突付き移動（Day2 の復習） --------------------------------
        nx = self.px + self.vx
        if not self.rect_collides_with_walls(nx, self.py):
            self.px = nx
        ny = self.py + self.vy
        if not self.rect_collides_with_walls(self.px, ny):
            self.py = ny

        # --- カメラ追従（Day1 の復習） ----------------------------------
        self.cam[0] = max(0, self.px - self.width / 2)
        self.cam[1] = max(0, self.py - self.height / 2)

        # --- エンカウント判定（B/F さん） -------------------------------
        player_rect = (self.px, self.py, self.w, self.h)
        enemy = find_touched_enemy(player_rect, self.enemies)
        if enemy is not None:
            self.start_battle(enemy)

    # ------------------------------------------------------------------
    # バトル開始処理 – 主に F さん担当（C/D/E さんの成果物を使う）
    # ------------------------------------------------------------------
    def start_battle(self, enemy: EnemySymbol):
        """
        1. フィールドモード → バトルモードに切り替える
        2. BattleStatus を初期化する
        3. ログに「エンカウントしました！」と出す
        """
        self.mode = "battle"
        self.current_enemy = enemy
        self.enemy_status = BattleStatus(enemy.name, enemy.max_hp, enemy.attack)
        self.battle_turn = "player"
        self.battle_log = [
            f"{enemy.name} があらわれた！",
            "スペースキーで『こうげき』できます。",
        ]

    # ------------------------------------------------------------------
    # バトル更新 – 主に C/D/E さん担当
    # ------------------------------------------------------------------
    def update_battle(self, dt):
        # プレイヤーのターン：スペースキーで攻撃
        if self.battle_turn == "player":
            if "spacebar" in self.keys or " " in self.keys:
                self.player_attack()
        # 敵のターン：ちょっと待ってから自動攻撃、などの発展も可能
        elif self.battle_turn == "enemy":
            # 今回はシンプルに、もう一度スペースキーが押されたら敵ターンにする など
            if "spacebar" in self.keys or " " in self.keys:
                self.enemy_attack()

    def player_attack(self):
        if not self.enemy_status or not self.current_enemy:
            return
        damage = self.player_status.attack
        self.enemy_status.apply_damage(damage)
        self.battle_log.append(
            f"{self.player_status.name} のこうげき！ {self.enemy_status.name} に {damage} ダメージ！"
        )
        if self.enemy_status.is_dead():
            self.battle_log.append(f"{self.enemy_status.name} をたおした！")
            # フィールド上の敵も「たおした」フラグに
            self.current_enemy.defeated = True
            # バトル終了 → フィールドへ戻る
            self.mode = "field"
            self.current_enemy = None
            self.enemy_status = None
        else:
            self.battle_turn = "enemy"
            self.battle_log.append("敵のターン！（スペースキーでもう一度進める）")

    def enemy_attack(self):
        if not self.enemy_status or not self.current_enemy:
            return
        damage = self.enemy_status.attack
        self.player_status.apply_damage(damage)
        self.battle_log.append(
            f"{self.current_enemy.name} のこうげき！ {self.player_status.name} は {damage} ダメージ！"
        )
        if self.player_status.is_dead():
            self.battle_log.append(f"{self.player_status.name} は たおれてしまった……")
            self.mode = "field"  # 簡単のためフィールドに戻すだけ（ゲームオーバー画面は発展課題）
        else:
            self.battle_turn = "player"
            self.battle_log.append("あなたのターン！（スペースキーでこうげき）")

    # ------------------------------------------------------------------
    # 画面描画 – 主に D さん担当（バトル UI / HP 表示など）
    # ------------------------------------------------------------------
    def draw(self):
        self.canvas.clear()
        with self.canvas:
            # 背景
            Color(*BG)
            Rectangle(pos=self.pos, size=self.size)

            # --- タイルマップ（Day1 の復習） ----------------------------
            ts = TILE_SIZE
            Color(1, 1, 1, 1)
            PushMatrix()
            Translate(-self.cam[0], -self.cam[1])

            for r, row in enumerate(self.grid):
                for c, tid in enumerate(row):
                    if 0 <= tid < len(self.tiles):
                        Rectangle(
                            texture=self.tiles[tid],
                            pos=(c * ts, r * ts),
                            size=(ts, ts),
                        )

            # --- 敵シンボル描画（A さん担当） ----------------------------
            for enemy in self.enemies:
                if enemy.defeated:
                    continue
                ex, ey = enemy.pos_px
                Color(0.9, 0.2, 0.2, 1.0)
                Rectangle(pos=(ex, ey), size=(ts - 6, ts - 6))

            # --- プレイヤー描画 -----------------------------------------
            Color(0.35, 0.67, 1.0, 1.0)
            Rectangle(pos=(self.px, self.py), size=(self.w, self.h))

            PopMatrix()

            # --- 画面下のバトル UI --------------------------------------
            if self.mode == "battle":
                self.draw_battle_panel()

    def draw_battle_panel(self):
        """画面下 1/3 をバトル用のウィンドウとして使う。"""
        panel_h = self.height * 0.35
        panel_y = 0
        # パネル背景
        Color(0, 0, 0, 0.7)
        Rectangle(pos=(0, panel_y), size=(self.width, panel_h))

        # HP 表示（C さん）
        # 左側：プレイヤー
        Color(1, 1, 1, 1)
        player_text = f"{self.player_status.name} HP: {self.player_status.hp}/{self.player_status.max_hp}"
        # 右側：敵（存在する場合）
        enemy_text = ""
        if self.enemy_status:
            enemy_text = f"{self.enemy_status.name} HP: {self.enemy_status.hp}/{self.enemy_status.max_hp}"

        # 簡易的に Label を 2 つ置く代わりに、DebugHUD ラベルを再利用してもOK。
        # ここではシンプルに Kivy の Label を使うサンプルをコメントとして載せておきます。
        #
        # from kivy.uix.label import Label
        # self.add_widget(Label(text=player_text, pos=(16, panel_h-32)))
        # self.add_widget(Label(text=enemy_text, pos=(self.width/2, panel_h-32)))
        #
        # 実際の授業では、先生と相談して UI 部分をクラス分割しても良いです。

        # コマンド＆ログ（E さん）
        log_lines = list(self.battle_log)[-3:]  # 最後の 3 行だけ表示
        base_y = panel_h - 64
        for i, line in enumerate(log_lines):
            y = panel_y + base_y - i * 24
            # 文字を描くのは Label クラスの役割なので、ここでは簡単に debug_label を使う
            # → 文字列は update_debug_text() でまとめて表示する

        # ※実際の授業では、battle_log の内容を画面下にラベルで表示する実装を
        #    D/E さんに任せてもOKです。このサンプルはあくまで構造イメージです。

    

    # ------------------------------------------------------------------
    # デバッグ用テキスト（簡易ログ表示もここでまとめて行う）
    # ------------------------------------------------------------------
    def update_debug_text(self):
        lines = []
        lines.append(f"mode={self.mode}")
        lines.append(f"player=({self.px:.1f},{self.py:.1f})")
        if self.current_enemy:
            lines.append(f"enemy={self.current_enemy.name} pos=({self.current_enemy.tile_x},{self.current_enemy.tile_y})")
        lines.append(f"HP: {self.player_status.hp}/{self.player_status.max_hp}")
        # battle_log の最後の 2 行だけオマケで表示
        if self.battle_log:
            tail = list(self.battle_log)[-2:]
            lines.append("--- log ---")
            lines.extend(tail)
        self.debug_label.text = "\n".join(lines)


class Day5App(App):
    def build(self):
        return Game()


if __name__ == "__main__":
    Day5App().run()
