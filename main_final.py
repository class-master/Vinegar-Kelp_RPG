# -*- coding: utf-8 -*-
"""
Vinegar-Kelp_RPG 統合版（宝箱探索RPG・最小で動くギブス版）

目的：
    - Day5（探索→戦闘）と Day6（宝箱→所持品→使用）を「1本の作品」に統合する
    - 発表で語れる“芯”を固定する：宝箱を集めてクリアする探索RPG

ギブス（固定ルール）：
    - main は1本（このファイル）
    - mode は "field" / "battle" / "clear" / "gameover" のみ
    - クリア条件：宝箱を全て開ける
    - ゲームオーバー：HPが0

操作：
    - 矢印/WASD：移動
    - E：宝箱を開ける（隣接）
    - I：所持品ウィンドウ開閉
    - U：所持品の先頭アイテムを使用（回復）
    - SPACE：バトルで攻撃（簡易）
    - R：クリア/ゲームオーバー時にリスタート
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty

from config import WIDTH, HEIGHT, TILE_SIZE, BG
from map_loader_kivy import load_csv_as_tilemap, load_tileset_regions
from items_day6 import ITEMS
from systems.use_item import use_item
from ui.inventory_window import InventoryWindow


# マップ（いまは steel_map01 を使う。field.csv でもOK）
MAP_CSV = "assets/maps/steel_map01.csv"
TILESET_PNG = "assets/maps/steel_tileset.png"


# ----------------------------------------------------------------------
# データ（敵・宝箱）
# ----------------------------------------------------------------------
@dataclass
class EnemySymbol:
    name: str
    tile_x: int
    tile_y: int
    max_hp: int = 10
    attack: int = 3
    defeated: bool = False


@dataclass
class Chest:
    tile_x: int
    tile_y: int
    item_id: str
    opened: bool = False


# 宝箱の配置（デモ用の最小）
# ※マップサイズや壁配置により、開けられない位置だと辛いので「通路に置く」寄せを推奨
DEFAULT_CHESTS: List[Chest] = [
    Chest(6, 6, "potion"),
    Chest(10, 8, "potion"),
    Chest(14, 10, "hi_potion"),
    Chest(18, 12, "potion"),
    Chest(22, 14, "hi_potion"),
]


DEFAULT_ENEMIES: List[EnemySymbol] = [
    EnemySymbol("スライム", 10, 6, max_hp=12, attack=3),
    EnemySymbol("コウモリ", 14, 8, max_hp=8, attack=4),
    EnemySymbol("キノコ", 18, 11, max_hp=10, attack=3),
]


def is_adjacent_tile(ax: int, ay: int, bx: int, by: int) -> bool:
    """上下左右に1マス隣なら True（斜めは不可）"""
    return abs(ax - bx) + abs(ay - by) == 1


def inventory_to_lines(inventory: Dict[str, int]) -> List[str]:
    lines: List[str] = []
    for item_id, count in sorted(inventory.items()):
        name = ITEMS.get(item_id, {}).get("name", item_id)
        lines.append(f"{name} x{count}")
    return lines


# ----------------------------------------------------------------------
# ゲーム本体
# ----------------------------------------------------------------------
class Game(Widget):
    # ログはPropertyにしておくとデバッグしやすい
    battle_log = ListProperty([])
    mode = StringProperty("field")  # "field" / "battle" / "clear" / "gameover"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.size = (WIDTH, HEIGHT)

        # マップ読み込み
        self.grid, self.rows, self.cols = load_csv_as_tilemap(MAP_CSV)
        self.tiles = load_tileset_regions(TILESET_PNG, TILE_SIZE, TILE_SIZE)

        # プレイヤー位置（タイル座標）
        self.px, self.py = 3, 3
        self.cam_x, self.cam_y = 0, 0

        # プレイヤーの戦闘ステータス（Day5互換の“辞書”形式へ寄せる）
        self.player_status = {"name": "主人公", "max_hp": 20, "hp": 20, "attack": 5}

        # 敵/宝箱/所持品
        self.enemies: List[EnemySymbol] = [EnemySymbol(e.name, e.tile_x, e.tile_y, e.max_hp, e.attack) for e in DEFAULT_ENEMIES]
        self.chests: List[Chest] = [Chest(c.tile_x, c.tile_y, c.item_id, opened=False) for c in DEFAULT_CHESTS]
        self.inventory: Dict[str, int] = {}

        # バトル状態
        self.current_enemy: Optional[EnemySymbol] = None
        self.enemy_status: Optional[Dict[str, int]] = None  # {"name","max_hp","hp","attack"}

        # UI：所持品ウィンドウ
        self.inv_window = InventoryWindow()
        self.inv_window.pos = (10, HEIGHT - self.inv_window.height - 10)
        self.add_widget(self.inv_window)

        # UI：固定HUD（右上）
        self.hud = Label(
            text="",
            size_hint=(None, None),
            size=(360, 120),
            pos=(WIDTH - 370, HEIGHT - 130),
            halign="left",
            valign="top",
        )
        self.hud.bind(size=lambda *_: setattr(self.hud, "text_size", self.hud.size))
        self.add_widget(self.hud)

        # キー入力
        self.keys = set()
        Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)

        # 更新ループ
        Clock.schedule_interval(self.update, 1.0 / 30.0)

        # 初回描画
        self._refresh_ui()
        self.draw()

    # ----------------------------
    # 入力
    # ----------------------------
    def _on_key_down(self, window, keycode, scancode, codepoint, modifiers):
        key_id, s = keycode

        # どのmodeでも使うキー
        if s == "i":
            self.inv_window.toggle()
            self._refresh_ui()
            return True
        if s == "u":
            self._try_use_first_item()
            return True
        if s == "e" and self.mode == "field":
            self._try_open_chest()
            return True
        if s == "r" and self.mode in ("clear", "gameover"):
            self._restart()
            return True

        # mode別
        if self.mode == "battle":
            if s == "space":
                self._battle_player_attack()
            return True

        # 移動（fieldのみ）
        if self.mode == "field":
            self.keys.add(s)
        return True

    def _on_key_up(self, window, keycode):
        key_id, s = keycode
        if s in self.keys:
            self.keys.remove(s)
        return True

    # ----------------------------
    # 更新
    # ----------------------------
    def update(self, dt):
        if self.mode == "field":
            self._update_field(dt)
        # battle は入力駆動（space）なので dt 更新は最小
        self._refresh_ui()
        self.draw()

    def _update_field(self, dt):
        # 速度（タイル座標でなくピクセルっぽく動かす必要がある場合はここを拡張）
        # 今回は教材の簡便さ優先で「タイル移動」寄せにする
        dx, dy = 0, 0
        if "w" in self.keys or "up" in self.keys:
            dy = 1
        elif "s" in self.keys or "down" in self.keys:
            dy = -1
        elif "a" in self.keys or "left" in self.keys:
            dx = -1
        elif "d" in self.keys or "right" in self.keys:
            dx = 1

        if dx == 0 and dy == 0:
            return

        nx, ny = self.px + dx, self.py + dy
        if not self._tile_is_walkable(nx, ny):
            return

        self.px, self.py = nx, ny

        # 敵と接触 → バトル開始
        for enemy in self.enemies:
            if enemy.defeated:
                continue
            if enemy.tile_x == self.px and enemy.tile_y == self.py:
                self._start_battle(enemy)
                break

    # ----------------------------
    # 判定
    # ----------------------------
    def _tile_is_walkable(self, tx: int, ty: int) -> bool:
        if tx < 0 or ty < 0 or tx >= self.cols or ty >= self.rows:
            return False
        # 壁タイルは 1 を想定（教材ルール）
        tile = self.grid[ty][tx]
        return tile == 0

    # ----------------------------
    # 宝箱
    # ----------------------------
    def _try_open_chest(self):
        """隣接している未開封宝箱を開ける"""
        for chest in self.chests:
            if chest.opened:
                continue
            if is_adjacent_tile(self.px, self.py, chest.tile_x, chest.tile_y):
                chest.opened = True
                self.inventory[chest.item_id] = self.inventory.get(chest.item_id, 0) + 1
                name = ITEMS.get(chest.item_id, {}).get("name", chest.item_id)
                self._log(f"宝箱を開けた！ {name}を手に入れた。")
                self._refresh_inventory_lines()
                self._check_clear()
                return

        self._log("（近くに宝箱がない…）")

    def _check_clear(self):
        if all(c.opened for c in self.chests):
            self.mode = "clear"
            self._log("宝箱を全部あつめた！ CLEAR！")

    # ----------------------------
    # 所持品
    # ----------------------------
    def _refresh_inventory_lines(self):
        self.inv_window.set_items(inventory_to_lines(self.inventory))

    def _try_use_first_item(self):
        """所持品の先頭（ソート順）を1つ使用する。"""
        if not self.inventory:
            self._log("所持品がない…")
            self._refresh_inventory_lines()
            return

        item_id = sorted(self.inventory.keys())[0]
        ok, msg = use_item(self.inventory, item_id, self.player_status, ITEMS)
        self._log(msg)
        self._refresh_inventory_lines()

    # ----------------------------
    # バトル（簡易FF風）
    # ----------------------------
    def _start_battle(self, enemy: EnemySymbol):
        self.mode = "battle"
        self.current_enemy = enemy
        self.enemy_status = {"name": enemy.name, "max_hp": enemy.max_hp, "hp": enemy.max_hp, "attack": enemy.attack}
        self.battle_log = [f"{enemy.name}があらわれた！", "SPACEでこうげき！"]

    def _battle_player_attack(self):
        if self.enemy_status is None or self.current_enemy is None:
            return

        # プレイヤー攻撃
        dmg = self.player_status.get("attack", 3)
        self.enemy_status["hp"] = max(0, self.enemy_status["hp"] - dmg)
        self.battle_log.append(f"主人公のこうげき！ {dmg}ダメージ！")

        if self.enemy_status["hp"] <= 0:
            self.battle_log.append(f"{self.enemy_status['name']}をたおした！")
            self.current_enemy.defeated = True
            self.mode = "field"
            self.current_enemy = None
            self.enemy_status = None
            return

        # 敵の反撃
        edmg = self.enemy_status.get("attack", 2)
        self.player_status["hp"] = max(0, self.player_status["hp"] - edmg)
        self.battle_log.append(f"{self.enemy_status['name']}のこうげき！ {edmg}ダメージ！")

        if self.player_status["hp"] <= 0:
            self.mode = "gameover"
            self.battle_log.append("あなたはたおれた……")
            self._log("GAME OVER（Rでリスタート）")

    # ----------------------------
    # ユーティリティ
    # ----------------------------
    def _restart(self):
        # ざっくり初期化（“作品として動く”を優先）
        self.mode = "field"
        self.px, self.py = 3, 3
        self.player_status["hp"] = self.player_status["max_hp"]
        self.inventory.clear()
        for e in self.enemies:
            e.defeated = False
        for c in self.chests:
            c.opened = False
        self.current_enemy = None
        self.enemy_status = None
        self.battle_log = ["リスタートした！"]
        self._refresh_inventory_lines()

    def _log(self, msg: str):
        # バトルログに混ぜて「発表で見えるログ」を優先
        self.battle_log.append(msg)
        # 長くなりすぎると見にくいので末尾だけ残す
        if len(self.battle_log) > 10:
            self.battle_log = self.battle_log[-10:]

    def _refresh_ui(self):
        opened = sum(1 for c in self.chests if c.opened)
        total = len(self.chests)
        inv = inventory_to_lines(self.inventory)

        # HUDは短く・要点だけ
        lines = []
        lines.append(f"HP: {self.player_status['hp']}/{self.player_status['max_hp']}")
        lines.append(f"宝箱: {opened}/{total}")
        lines.append("")
        lines.append("操作：WASD/矢印 移動")
        lines.append("E: 宝箱   I: 所持品   U: 使用")
        if self.mode == "battle":
            lines.append("SPACE: こうげき")
        if self.mode in ("clear", "gameover"):
            lines.append("R: リスタート")
        self.hud.text = "\n".join(lines)

        # 所持品内容更新
        self._refresh_inventory_lines()

    # ----------------------------
    # 描画
    # ----------------------------
    def draw(self):
        ts = TILE_SIZE

        # カメラ（プレイヤー中心）
        target_x = self.px * ts - WIDTH // 2 + ts // 2
        target_y = self.py * ts - HEIGHT // 2 + ts // 2
        self.cam_x = int(target_x)
        self.cam_y = int(target_y)

        self.canvas.clear()

        with self.canvas:
            # 背景
            Color(*BG)
            Rectangle(pos=(0, 0), size=(WIDTH, HEIGHT))

            # タイル
            # grid は [row][col] で row は y（下→上じゃない可能性あり。見た目優先でそのまま描く）
            for ty in range(self.rows):
                for tx in range(self.cols):
                    tile_id = self.grid[ty][tx]
                    # tile_id が 0/1 以外でもOK（tilesetにあるなら描ける）
                    if tile_id in self.tiles:
                        rect = self.tiles[tile_id]
                        # Kivyの座標系は左下原点なので y を反転して表示するほうが“上が上”に見える
                        draw_y = (self.rows - 1 - ty) * ts - self.cam_y
                        draw_x = tx * ts - self.cam_x
                        Rectangle(texture=rect.texture, pos=(draw_x, draw_y), size=(ts, ts))
                    else:
                        # tileset 未対応のタイルは色で補う
                        if tile_id == 1:
                            Color(0.2, 0.2, 0.2, 1)
                        else:
                            Color(0.1, 0.1, 0.1, 1)
                        draw_y = (self.rows - 1 - ty) * ts - self.cam_y
                        draw_x = tx * ts - self.cam_x
                        Rectangle(pos=(draw_x, draw_y), size=(ts, ts))

            # 宝箱（未開封は黄色、開封済みは暗色）
            for chest in self.chests:
                draw_y = (self.rows - 1 - chest.tile_y) * ts - self.cam_y
                draw_x = chest.tile_x * ts - self.cam_x
                if chest.opened:
                    Color(0.4, 0.3, 0.1, 1)
                else:
                    Color(0.9, 0.7, 0.2, 1)
                Rectangle(pos=(draw_x + 6, draw_y + 6), size=(ts - 12, ts - 12))

            # 敵（未撃破のみ赤）
            for enemy in self.enemies:
                if enemy.defeated:
                    continue
                draw_y = (self.rows - 1 - enemy.tile_y) * ts - self.cam_y
                draw_x = enemy.tile_x * ts - self.cam_x
                Color(0.9, 0.2, 0.2, 1)
                Rectangle(pos=(draw_x + 6, draw_y + 6), size=(ts - 12, ts - 12))

            # プレイヤー（水色）
            py = (self.rows - 1 - self.py) * ts - self.cam_y
            px = self.px * ts - self.cam_x
            Color(0.2, 0.8, 0.9, 1)
            Rectangle(pos=(px + 4, py + 4), size=(ts - 8, ts - 8))

            # バトル用の暗幕
            if self.mode == "battle":
                Color(0, 0, 0, 0.65)
                Rectangle(pos=(0, 0), size=(WIDTH, HEIGHT))

        # バトルログ表示（Labelはcanvas外：Widgetツリーで保持するのが楽）
        # ここでは「HUDに寄せる」ため、battle_log をHUDの下に出す簡易方式
        if self.mode == "battle":
            # HUDの下に battle_log を追加表示
            bl = "\n".join(self.battle_log[-6:])
            self.hud.text = self.hud.text + "\n\n" + bl


class FinalApp(App):
    def build(self):
        return Game()


if __name__ == "__main__":
    FinalApp().run()
