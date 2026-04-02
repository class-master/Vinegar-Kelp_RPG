# -*- coding: utf-8 -*-
"""
目的: Title画面の最小実装。ボタン1つで Town へ移動できればOK。
前提: ScreenManager に "town" という名前の画面が登録されていること。
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

class TitleScreen(MDScreen):
    def on_pre_enter(self, *args):
        # ★ヒント: 画面が入る直前に UI を作ると、戻ってきた時も毎回綺麗に描き直せる。
        self.clear_widgets()
        layout = MDBoxLayout(orientation="vertical", spacing="16dp", padding="24dp")
        layout.add_widget(MDLabel(text="Vinegar-Kelp_RPG", halign="center", font_style="H4"))
        layout.add_widget(MDLabel(text="Title Screen", halign="center"))
        # ★ヒント: ボタンの on_release で self.go_town を呼ぶ → manager.current を書き換える。
        layout.add_widget(MDRectangleFlatButton(text="Start (Go Town)", pos_hint={"center_x": 0.5}, on_release=self.go_town))
        self.add_widget(layout)

    def go_town(self, *args):
        self.manager.current = "town"
        if hasattr(self.manager, "play_screen_bgm"):
            self.manager.play_screen_bgm("town")