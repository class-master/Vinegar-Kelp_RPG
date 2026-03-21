# events/loader.py
# マップ上のイベント（看板、NPC、宝箱など）を管理・読み込みするモジュールです。

import json
from pathlib import Path

class EventManager:
    """
    マップ上のイベントを読み込み、管理するクラスです。
    """
    def __init__(self):
        self.events = {}  # (x, y) 座標をキーにしてイベント情報を保持します

    def load_events(self, map_name):
        """
        指定されたマップ名に対応するイベントデータをJSONから読み込みます。
        例: data/events/map1.json
        """
        self.events = {}
        # 修正：パスはプロジェクトの構成に合わせて調整してくださいね
        event_file = Path(f"data/events/{map_name}.json")
        
        if not event_file.exists():
            print(f"通知: イベントファイル {event_file} が見つかりませんでしたわ。")
            return

        try:
            with open(event_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    # 座標をタプルにしてキーにします（衝突判定を楽にするためですわ）
                    pos = (item["x"], item["y"])
                    self.events[pos] = {
                        "type": item.get("type", "message"),
                        "content": item.get("content", ""),
                        "enemy_id": item.get("enemy_id", None) # 戦闘イベント用
                    }
        except Exception as e:
            print(f"エラー: イベントの読み込みに失敗しましたわ。 {e}")

    def get_event(self, x, y):
        """
        指定された座標にイベントがあるか確認し、あればその内容を返します。
        """
        return self.events.get((x, y))

# --- 使用例（テスト用） ---
if __name__ == "__main__":
    manager = EventManager()
    # manager.load_events("map1")