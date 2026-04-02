# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import csv

from kivymd.uix.screen import MDScreen

from ui.widgets.map_widget import MapWidget


BASE_DIR = Path(__file__).resolve().parent.parent  # プロジェクト直下想定


def load_collision_csv(path: Path) -> list[list[int]] | None:
    """0/1 のCSVを読み込む。読めなければ None（落とさない）"""
    try:
        if not path.exists():
            print(f"[WARN] collision csv not found: {path}")
            return None
        with path.open("r", encoding="utf-8", newline="") as f:
            rows = [[int(v) for v in row] for row in csv.reader(f) if row]
        if not rows:
            print(f"[WARN] collision csv is empty: {path}")
            return None
        # 形状チェック（行の長さが揃ってないときは落とさず None）
        w = len(rows[0])
        if any(len(r) != w for r in rows):
            print(f"[WARN] collision csv has ragged rows: {path}")
            return None
        return rows
    except Exception as e:
        print(f"[WARN] collision csv load failed: {path} ({e})")
        return None


class TownScreen(MDScreen):
    """
    TownScreen（表示の器）
    - town_view.png（見た目）
    - town_collision.csv（0/1の当たり判定）
    を読み、MapWidgetに注入する（DI）
    """

    def on_pre_enter(self, *args):
        view_path = BASE_DIR / "assets" / "maps" / "town_view.png"
        col_path = BASE_DIR / "assets" / "maps" / "town_collision.csv"

        collision = load_collision_csv(col_path)

        self.clear_widgets()
        self.add_widget(
            MapWidget(
                view_path=view_path,
                collision=collision,
            )
        )