# -*- coding: utf-8 -*-
"""
scenes/title.py – タイトル（# [E]）
STEP1: Enter でフィールドへ遷移
STEP2: Esc で終了
ヒント: `Window.request_keyboard` でキーボードを取得し、`on_key_down` を使う。
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

class TitleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical", padding=20, spacing=10)
        root.add_widget(Label(text="[b]Steel MasterD[/b]", markup=True, font_size="28sp"))
        root.add_widget(Label(text="Press [b]Enter[/b] → Field", markup=True))
        root.add_widget(Label(text="Press [b]Esc[/b] → Quit", markup=True))
        self.add_widget(root)

        self._kb = None
        Clock.schedule_once(self._bind, 0)

    def _bind(self, *_):
        # HINT: ここでキーボードを取得し on_key_down を bind します
        self._kb = Window.request_keyboard(self._kb_closed, self)
        if self._kb:
            self._kb.bind(on_key_down=self._on_key_down)

    def _kb_closed(self, *_):
        if self._kb:
            self._kb.unbind(on_key_down=self._on_key_down)
            self._kb = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key_id, key_str = keycode
        if key_str in ("enter", "numpadenter"):
            # HINT: ここで self.manager.current = "field"
            self.manager.current = "field"
            return True
        if key_str == "escape":
            from kivy.app import App
            App.get_running_app().stop()
            return True
        return False
