# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.uix.screenmanager import Screen

from ui.battle_window import BattleWindow
from systems.battle.battle_controller import BattleController


class BattleScreen(Screen):
    """
    BattleScreen = Viewホスト（画面遷移の器）

    - ScreenManager に載る “画面”
    - 戦闘UI本体は BattleWindow に委譲（描画・演出・ログ消費）
    - 戦闘進行は BattleController に委譲（ターン進行・ログ生成）
    - 依存は set_battle(...) で注入（DI）
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._window: BattleWindow | None = None
        self._controller: BattleController | None = None

    def set_battle(self, *, controller: BattleController, enemy_info=None):
        
        """DI: 戦闘をこの画面に接着する唯一の入口"""
        self._controller = controller

        # BattleWindowは“表示の責務”だけ
        if self._window is None:
            self._window = BattleWindow()
            self.clear_widgets()
            self.add_widget(self._window)

        # BattleWindowに “進行開始” を依頼（Controllerは注入済み）
        self._window.start_turn(self._controller, enemy_info=enemy_info)

    def on_pre_leave(self, *args):
        # ここでBGM停止やClock解除などが必要なら、BattleWindow側に委譲が安全
        return super().on_pre_leave(*args)