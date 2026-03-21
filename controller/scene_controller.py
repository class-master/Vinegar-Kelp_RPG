# controller/scene_controller.py

from kivy.uix.screenmanager import ScreenManager
from screens.title import TitleScreen
from screens.town import TownScreen
from screens.field import FieldScreen
from screens.battle import BattleScreen
from systems.audio.bgm_manager import BgmManager
from systems.battle.battle_controller import BattleController
from entities.status import Status
from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent.parent


class SceneController(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bgm = BgmManager()

        self.bgm_paths = {
            "town": "assets/sounds/fantasy_town.mp3",
            "field": "assets/sounds/fantasy_everyday.mp3",
            "battle_default": "assets/sounds/battle.mp3",
        }

        self.add_widget(TitleScreen(name="title"))
        self.add_widget(TownScreen(name="town"))
        self.add_widget(FieldScreen(name="field"))
        self.add_widget(BattleScreen(name="battle"))

        self.current = "title"
    
    
    def play_screen_bgm(self, screen_name: str):
        if screen_name == "town":
            self.bgm.play(self.bgm_paths["town"])
        elif screen_name == "field":
            self.bgm.play(self.bgm_paths["field"])
        
        
    def start_battle(self, enemy, player, enemy_info=None):
        """
        DI接着:
            SceneController -> BattleController(進行) -> BattleScreen(器) -> BattleWindow(UI)
        """
        # 1) Controller生成（ここが唯一の生成点）
        controller = BattleController(player=player, enemy=enemy)

        # 2) BattleScreen取得（ScreenManagerに登録済み前提）
        battle_screen: BattleScreen = self.get_screen("battle")  # nameは登録名に合わせる

        # 3) DI接着して遷移
        battle_screen.set_battle(controller=controller, enemy_info=enemy_info)
        self.current = "battle"

        battle_bgm = None
        if enemy_info:
            battle_bgm = enemy_info.get("bgm")
        if not battle_bgm:
            battle_bgm = self.bgm_paths["battle_default"]
            
        self.bgm.play(battle_bgm)
        self.current = "battle"

    def load_enemy_status(self, enemy_id: str):
        data_path = BASE_DIR / "data" / "input" / "enemies.json"
        data = json.loads(data_path.read_text(encoding="utf-8"))
        info = data[enemy_id]

        status = Status(
            name=info["name"],
            max_hp=info["max_hp"],
            attack=info["attack"],
            defense=info.get("defense", 0),
        )
        return status, info        
            
            
    def get_player_status(self) -> Status:
    # 今は最小固定（あとでセーブや成長に差し替え可能）
        return Status(name="Hero", max_hp=30, attack=8, defense=2)