# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from systems.battle.battle_controller import BattleController


# フォント登録
_FONT_PATH = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "GenShinGothic-Regular.ttf"
if _FONT_PATH.exists():
    try:
        LabelBase.register(name="GenShin", fn_regular=str(_FONT_PATH))
    except Exception:
        pass

# KV読み込み
Builder.load_file(str(Path(__file__).resolve().parent / "battle_window.kv"))


class BattleWindow(BoxLayout):
    enemy_image = StringProperty("")

    # 表示用
    message = StringProperty("コマンド？")
    command_text = StringProperty("▶ たたかう\n  にげる")

    player_name = StringProperty("Hero")
    player_hp = StringProperty("HP: ?")
    enemy_name = StringProperty("スライム")
    enemy_hp = StringProperty("HP: ?")

    # HPアニメ用
    display_player_hp = NumericProperty(0)
    display_enemy_hp = NumericProperty(0)
    _target_player_hp = NumericProperty(0)
    _target_enemy_hp = NumericProperty(0)

    # 制御
    mode = StringProperty("command")  # command / resolving / finished
    _controller = ObjectProperty(None, rebind=True)
    _event = ObjectProperty(None, allownone=True)

    # コマンド選択
    _commands = ("たたかう", "にげる")
    _selected_index = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_key_down=self._on_key_down)

    def on_parent(self, *args):
        if self.parent is None:
            try:
                Window.unbind(on_key_down=self._on_key_down)
            except Exception:
                pass

    # ----------------------------
    # 戦闘開始
    # ----------------------------
    def start_turn(self, controller: BattleController, enemy_info=None):
        """
        戦闘開始時は自動で殴り合わない。
        まず command モードで止める。
        """
        self._controller = controller
        self._controller.start()

        self.player_name = controller.player.name
        self.enemy_name = controller.enemy.name
        self.enemy_image = enemy_info.get("image", "") if enemy_info else ""

        self.display_player_hp = controller.player.hp
        self.display_enemy_hp = controller.enemy.hp
        self._target_player_hp = controller.player.hp
        self._target_enemy_hp = controller.enemy.hp

        self.player_hp = f"HP: {self.display_player_hp}"
        self.enemy_hp = f"HP: {self.display_enemy_hp}"

        self.mode = "command"
        self._selected_index = 0
        self._refresh_command_text()
        self.message = "コマンド？"

        if self._event is not None:
            try:
                self._event.cancel()
            except Exception:
                pass
            self._event = None

    # ----------------------------
    # コマンド表示
    # ----------------------------
    def _refresh_command_text(self):
        lines = []
        for i, cmd in enumerate(self._commands):
            cursor = "▶ " if i == self._selected_index else "  "
            lines.append(f"{cursor}{cmd}")
        self.command_text = "\n".join(lines)

    # ----------------------------
    # 入力
    # ----------------------------
    def _on_key_down(self, _window, key, scancode, codepoint, modifiers):
        if self.parent is None:
            return False

        if self.mode == "finished":
            return False

        if self.mode == "command":
            # 上
            if key == 273 or codepoint in ("w", "W"):
                self._selected_index = (self._selected_index - 1) % len(self._commands)
                self._refresh_command_text()
                return True

            # 下
            if key == 274 or codepoint in ("s", "S"):
                self._selected_index = (self._selected_index + 1) % len(self._commands)
                self._refresh_command_text()
                return True

            # 決定
            if key in (13, 32, 271):  # Enter / Space / Numpad Enter
                if self._selected_index == 0:
                    self._do_attack()
                else:
                    self._do_escape()
                return True

            # Esc は にげる
            if key == 27:
                self._do_escape()
                return True

        return False

    # ----------------------------
    # コマンド処理
    # ----------------------------
    def _do_attack(self):
        if not self._controller:
            return

        self.mode = "resolving"
        self.message = "たたかう！"

        # ここで初めて1ターン処理
        self._controller.take_turn()

        # ログを時間差で流す
        self._event = Clock.schedule_interval(self._consume_log, 0.8)

    def _do_escape(self):
        self.mode = "finished"
        self.command_text = ""
        self.message = "にげだした！"

        if self.parent and self.parent.manager:
            self.parent.manager.current = "field"
            if hasattr(self.parent.manager, "play_screen_bgm"):
                self.parent.manager.play_screen_bgm("field")

    # ----------------------------
    # ログ消費
    # ----------------------------
    def _consume_log(self, dt):
        if not self._controller:
            self.mode = "command"
            self._selected_index = 0
            self._refresh_command_text()
            self.message = "コマンド？"
            return False

        # まだログがある間は1件ずつ流す
        if self._controller.has_log():
            log = self._controller.pop_log()
            if not log:
                # 想定外でも止まらず次ターンへ戻す
                self.mode = "command"
                self._selected_index = 0
                self._refresh_command_text()
                self.message = "コマンド？"
                return False

            self.show_message(log["text"])

            damage = log.get("damage", 0)
            critical = log.get("critical", False)
            target = log.get("target", "enemy")

            if damage:
                self.shake()
                self.show_damage_popup(damage, target, critical=critical)

            self.update_status(self._controller.player, self._controller.enemy)
            return True

        # ここに来た時点でログは空
        if self._event is not None:
            try:
                self._event.cancel()
            except Exception:
                pass
            self._event = None

        # 勝敗がついていれば終了処理
        if self._controller.is_finished():
            result = self._controller.winner()
            self.mode = "finished"
            self.command_text = ""

            if result == "player":
                self.message = f"{self.enemy_name}を たおした！"
            else:
                self.message = "ぜんめつした…"

            if self.parent and self.parent.manager:
                Clock.schedule_once(self._return_to_field, 1.0)
            return False

        # 勝敗がついていないなら、必ず次のコマンド待ちへ戻す
        self.mode = "command"
        self._selected_index = 0
        self._refresh_command_text()
        self.message = "コマンド？"
        return False
    
    
    def shake(self, strength=dp(10), duration=0.05):
        stage = self.ids.battle_stage
        original_x = stage.x

        anim = (
            Animation(x=original_x - strength, duration=duration) +
            Animation(x=original_x + strength, duration=duration) +
            Animation(x=original_x - strength / 2, duration=duration) +
            Animation(x=original_x, duration=duration)
        )
        anim.start(stage)
    
    def _return_to_field(self, dt):
        if self.parent and self.parent.manager:
            self.parent.manager.current = "field"
            if hasattr(self.parent.manager, "play_screen_bgm"):
                self.parent.manager.play_screen_bgm("field")
    
    # ----------------------------
    # 表示更新
    # ----------------------------
    def update_status(self, player_status, enemy_status):
        self._target_player_hp = player_status.hp
        self._target_enemy_hp = enemy_status.hp
        Clock.schedule_interval(self._animate_hp, 0.05)

    def _animate_hp(self, dt):
        finished = True

        if self.display_player_hp > self._target_player_hp:
            self.display_player_hp -= 1
            finished = False

        if self.display_enemy_hp > self._target_enemy_hp:
            self.display_enemy_hp -= 1
            finished = False

        self.player_hp = f"HP: {self.display_player_hp}"
        self.enemy_hp = f"HP: {self.display_enemy_hp}"

        if finished:
            return False

    def show_message(self, text: str):
        self.message = text

    # ----------------------------
    # ダメージ演出（簡易）
    # ----------------------------
    def show_damage_popup(self, damage, target, critical=False):
        label = Label(
            text=str(damage),
            font_name="GenShin",
            font_size="32sp",
            color=(1, 0, 0, 1),
            size_hint=(None, None),
            size=(dp(100), dp(50)),
        )

        stage = self.ids.battle_stage

        if target == "enemy":
            label.center = (stage.width * 0.50, stage.height * 0.55)
        else:
            label.center = (stage.width * 0.22, stage.height * 0.30)

        stage.add_widget(label)

        anim = Animation(y=label.y + dp(40), opacity=0, duration=0.8)
        anim.bind(on_complete=lambda *x: stage.remove_widget(label))
        anim.start(label)