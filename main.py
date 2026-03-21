# -*- coding: utf-8 -*-
from pathlib import Path

from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

from config import WIDTH, HEIGHT
from controller.scene_controller import SceneController


# フォント（無ければ落とさない：教材向けの余白）
_FONT_PATH = Path(__file__).resolve().parent / "assets" / "fonts" / "GenShinGothic-Regular.ttf"
if _FONT_PATH.exists():
    LabelBase.register(name="GenShin", fn_regular=str(_FONT_PATH))


class MainApp(MDApp):
    def build(self):

        base = Path(__file__).resolve().parent
        resource_add_path(str(base))
        resource_add_path(str(base / "assets"))
        Window.size = (WIDTH, HEIGHT)

        # フォントを入れていれば適用（無ければデフォで続行）
        try:
            if "GenShin" in LabelBase._fonts:  # type: ignore[attr-defined]
                self.theme_cls.font_styles["Body1"] = ["GenShin", 16, False, 0.15]
        except Exception:
            pass

        return SceneController()


if __name__ == "__main__":
    MainApp().run()