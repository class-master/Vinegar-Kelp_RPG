# -*- coding: utf-8 -*-
from __future__ import annotations

from kivy.core.audio import SoundLoader


class BgmManager:
    """BGMを1本だけ管理する簡易マネージャ"""

    def __init__(self):
        self._sound = None
        self._current_path = ""

    def play(self, path: str | None, volume: float = 0.7) -> None:
        if not path:
            self.stop()
            return

        # 同じ曲なら再生し直さない
        if self._current_path == path and self._sound:
            if self._sound.state != "play":
                self._sound.play()
            return

        self.stop()

        sound = SoundLoader.load(path)
        if not sound:
            print(f"[BGM] load failed: {path}")
            return

        sound.volume = volume
        try:
            sound.loop = True
        except Exception:
            pass

        sound.play()
        self._sound = sound
        self._current_path = path
        print(f"[BGM] playing: {path}")

    def stop(self) -> None:
        if self._sound:
            try:
                self._sound.stop()
            except Exception:
                pass
        self._sound = None
        self._current_path = ""