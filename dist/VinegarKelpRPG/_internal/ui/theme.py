# -*- coding: utf-8 -*-
"""
目的: アプリ全体の配色やスタイル（KivyMDのテーマ）をまとめて設定する。
ヒント: 色の好みは人それぞれ。まずは読みやすさ優先でOK！
"""
def apply_theme(app):
    app.theme_cls.primary_palette = "Green"  # 他に "Blue", "Purple" などもあるよ
    app.theme_cls.primary_hue = "600"
    app.theme_cls.theme_style = "Dark"      # "Light" にすると雰囲気が変わる！
