# -*- coding: utf-8 -*-
"""
ui/hud.py – デバッグ HUD（# [D]）
STEP1: set_info(dict) でテキストを更新
STEP2: H キーで可視/不可視のトグル（visible=True/False）
"""
from kivy.uix.label import Label
from kivy.properties import BooleanProperty

class DebugHUD(Label):
    visible = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.font_size = "16sp"
        self.text = ""
        self.halign = "left"
        self.valign = "top"
        self.padding = (8, 8)

    def set_info(self, info: dict):
        # HINT: 必要なキー例 x,y,dir,fps,tile_x,tile_y
        x = info.get("x", 0.0)
        y = info.get("y", 0.0)
        d = info.get("dir", "-")
        fps = info.get("fps", 0.0)
        tx = info.get("tile_x", 0)
        ty = info.get("tile_y", 0)
        self.text = (
            "[b]HUD[/b]\n"
            f"x={x:.1f}, y={y:.1f}, dir={d}\n"
            f"tile=({tx},{ty})\n"
            f"fps={fps:.1f}"
        )
        self.opacity = 1.0 if self.visible else 0.0
