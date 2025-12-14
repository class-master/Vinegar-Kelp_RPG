# -*- coding: utf-8 -*-
"""
Day6：所持品ウィンドウ（生徒用）

目的：
    画面に所持品を出す。今日は「最小で動くUI」を優先する。

仕様（最小）：
    - set_items(lines) で表示内容を更新
    - show/hide で表示切替
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class InventoryWindow(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (360, 220)
        self.pos = (16, 16)
        self.padding = 8

        # 半透明の背景
        with self.canvas.before:
            Color(0, 0, 0, 0.7)
            self._bg = Rectangle(pos=self.pos, size=self.size)

        self.label = Label(text="(empty)", halign="left", valign="top")
        self.label.bind(size=self._update_text_size)
        self.add_widget(self.label)

        # 初期は非表示
        self.visible = False
        self.opacity = 0
        self.disabled = True

        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _update_text_size(self, *args):
        self.label.text_size = (self.label.width, None)

    def set_items(self, lines):
        self.label.text = "\n".join(lines) if lines else "(empty)"

    def show(self):
        self.visible = True
        self.opacity = 1
        self.disabled = False

    def hide(self):
        self.visible = False
        self.opacity = 0
        self.disabled = True

    def toggle(self):
        if self.visible:
            self.hide()
        else:
            self.show()
