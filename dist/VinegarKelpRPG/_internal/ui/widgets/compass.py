# -*- coding: utf-8 -*-
"""
目的: 方向を文字で分かりやすく表示する最小コンパス。
伸びしろ: 画像アイコンに差し替えたり、アニメーションさせたりできるよ。
"""
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

ARROWS = {"N":"↑","E":"→","S":"↓","W":"←"}  # ★ヒント: ここを"画像"に変えるのもアリ！

class Compass(MDBoxLayout):
    direction = StringProperty("N")

    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", spacing="4dp", **kwargs)
        self.label = MDLabel(text=self._text(), halign="left")
        self.add_widget(self.label)
        # ★ヒント: direction が変わるたびに _update を呼ぶと、画面が最新状態になるよ。
        self.bind(direction=lambda *_: self._update())

    def _text(self):
        return f"Dir: {self.direction} {ARROWS.get(self.direction, '?')}"

    def _update(self):
        self.label.text = self._text()
