�ｻｿ# main_day4.py
# Day4 騾包ｽｨ繝ｻ螢ｹ繝ｵ郢ｧ�ｽ｣郢晢ｽｼ郢晢ｽｫ郢晏ｳｨ竊堤ｹ晁�後Κ郢晢ｽｫ郢ｧ雋槭�ｻ郢ｧ鬆大ｴ帷ｸｺ蛹ｻ�ｽ玖愾�ｽｸ闔会ｽ､陜ｪ譁舌�ｻ邵ｺ貅倪螺邵ｺ讎雁ｺ顔ｸｲ繝ｻ
#
# 陞ｳ貊�蝨邵ｺ�ｽｮ郢晏干ﾎ溽ｹｧ�ｽｸ郢ｧ�ｽｧ郢ｧ�ｽｯ郢晏現繝ｻ App郢ｧ�ｽｯ郢晢ｽｩ郢ｧ�ｽｹ郢ｧ繝ｻPlayer/NPC/郢晄ｧｭ繝｣郢晁挙�ｽｪ�ｽｭ邵ｺ�ｽｿ髴趣ｽｼ邵ｺ�ｽｿ鬮｢�ｽ｢隰ｨ�ｽｰ邵ｺ�ｽｮ
# 陷ｷ讎顔√邵ｺ�ｽｫ陷ｷ蛹ｻ�ｽ冗ｸｺ蟶吮ｻ隴厄ｽｸ邵ｺ閧ｴ驪､邵ｺ蛹ｻ窶ｻ闖ｴ�ｽｿ邵ｺ�ｽ｣邵ｺ�ｽｦ邵ｺ荳岩味邵ｺ霈費ｼ樒ｸｲ繝ｻ

from typing import Optional

# 陞ｳ貅倥�ｻ郢晢ｽｭ郢ｧ�ｽｸ郢ｧ�ｽｧ郢ｧ�ｽｯ郢晏現竊楢惺蛹ｻ�ｽ冗ｸｺ蟶吮ｻ import 郢ｧ蜻亥ｶ檎ｸｺ閧ｴ驪､邵ｺ蛹ｻ窶ｻ邵ｺ荳岩味邵ｺ霈費ｼ樒ｸｲ繝ｻ
from status_day4 import Status
from systems.battle.battle_engine import player_attack, enemy_attack
from ui.battle_window import BattleWindow
import json
from pathlib import Path

mode = "field"  # "field" 邵ｺ�ｽｾ邵ｺ貅倥�ｻ "battle"

player_status = None      # Status
enemy_status: Optional["Status"] = None
battle_window = None      # BattleWindow 郢ｧ�ｽ､郢晢ｽｳ郢ｧ�ｽｹ郢ｧ�ｽｿ郢晢ｽｳ郢ｧ�ｽｹ

def setup_game():
    """Day4 騾包ｽｨ邵ｺ�ｽｮ陋ｻ譎�謔�陋ｹ謔ｶﾂ繧�繝ｵ郢ｧ�ｽ｣郢晢ｽｼ郢晢ｽｫ郢晉甥繝ｻ邵ｺ�ｽｮ郢ｧ�ｽｻ郢昴�ｻ繝ｨ郢ｧ�ｽ｢郢昴�ｻ繝ｻ繝ｻ荵昴○郢昴�ｻ繝ｻ郢ｧ�ｽｿ郢ｧ�ｽｹ雋�髢�ｽ咏ｸｲ繝ｻ""
    global player_status, battle_window
    # TODO: Day3 邵ｺ�ｽｨ陷ｷ譴ｧ�ｽｧ蛟･竊鍋ｹ晁ｼ斐≦郢晢ｽｼ郢晢ｽｫ郢晏ｳｨ繝ｻ雋�髢�ｽ咏ｹｧ螳夲ｽ｡蠕娯鴬邵ｲ繝ｻ
    # 關薙�ｻ setup_field() 邵ｺ�ｽｮ郢ｧ蛹ｻ竕ｧ邵ｺ�ｽｪ鬮｢�ｽ｢隰ｨ�ｽｰ郢ｧ雋樔ｻ也ｸｺ�ｽｳ陷��ｽｺ邵ｺ蜷ｶﾂ繝ｻ

    # TODO: 陞ｳ貊�蝨邵ｺ�ｽｮ郢晏干ﾎ樒ｹｧ�ｽ､郢晢ｽ､郢晢ｽｼ陷ｷ髦ｪ�ｽ�郢昜ｻ｣ﾎ帷ｹ晢ｽ｡郢晢ｽｼ郢ｧ�ｽｿ邵ｺ�ｽｫ陷ｷ蛹ｻ�ｽ冗ｸｺ蟶吮ｻ髫ｱ�ｽｿ隰ｨ�ｽｴ邵ｺ蜷ｶ�ｽ狗ｸｲ繝ｻ
    # player_status = Status("郢ｧ繝ｻ竕ｧ邵ｺ蜉ｱ�ｽ�", max_hp=30, attack=8, defense=2)

    # TODO: 郢晢ｽｬ郢ｧ�ｽ､郢ｧ�ｽ｢郢ｧ�ｽｦ郢晏現竊楢惺蛹ｻ�ｽ冗ｸｺ蟶吮ｻ BattleWindow 郢ｧ蝣､蜃ｽ隰瑚�鯉ｼ邵ｺ�ｽｦ髴托ｽｽ陷会｣ｰ邵ｺ蜷ｶ�ｽ狗ｸｲ繝ｻ
    battle_window = BattleWindow()
    root_layout.add_widget(battle_window)
    battle_window.opacity = 0  # 隴崢陋ｻ譏ｴ繝ｻ鬮ｱ讚��ｽ｡�ｽｨ驕会ｽｺ邵ｺ�ｽｫ邵ｺ蜉ｱ窶ｻ邵ｺ鄙ｫ�ｿ･

def load_enemy_status(enemy_id: str):
    """enemies_day4.json 邵ｺ荵晢ｽ芽ｬｨ�ｽｵ郢ｧ�ｽｹ郢昴�ｻ繝ｻ郢ｧ�ｽｿ郢ｧ�ｽｹ郢ｧ繝ｻ闖ｴ轣倥�ｻ髫ｱ�ｽｭ邵ｺ�ｽｿ髴趣ｽｼ郢ｧ阮吶� Status 郢ｧ螳夲ｽｿ譁絶��隲�ｽｳ陞ｳ螢ｹﾂ繝ｻ""
    from status_day4 import Status
    import json
    from pathlib import Path

    data_path = Path("input/enemies_day4.json")
    data = json.loads(data_path.read_text(encoding="utf-8"))
    info = data[enemy_id]
    return Status(
        name=info["name"],
        max_hp=info["max_hp"],
        attack=info["attack"],
        defense=info.get("defense", 0),
    )

def start_battle(enemy_id: str):
    """Day4 邵ｺ�ｽｮ郢晁�後Κ郢晢ｽｫ鬮｢蜿･�ｽｧ蜿･繝ｻ騾�繝ｻﾂ繧磯峅郢ｧ�ｽｹ郢昴�ｻ繝ｻ郢ｧ�ｽｿ郢ｧ�ｽｹ郢ｧ蝣､逡題ｫ｢荳奇ｼ邵ｲ繧曵郢ｧ蛛ｵ繝ｰ郢晏現ﾎ晉ｹ晢ｽ｢郢晢ｽｼ郢晏ｳｨ竊鍋ｸｺ蜷ｶ�ｽ狗ｸｲ繝ｻ""
    global mode, enemy_status

    enemy_status = load_enemy_status(enemy_id)
    mode = "battle"

    if battle_window is not None and player_status is not None:
        battle_window.update_status(player_status, enemy_status)
        battle_window.show_message(f"{enemy_status.name} 邵ｺ蠕娯旺郢ｧ蟲ｨ�ｽ冗ｹｧ蠕娯螺繝ｻ繝ｻ)
        # battle_window.opacity = 1

def end_battle(message: str):
    """郢晁�後Κ郢晢ｽｫ驍ｨ繧��ｽｺ繝ｻ繝ｻ騾�繝ｻﾂ繧�ﾎ鍋ｹ昴�ｻ縺晉ｹ晢ｽｼ郢ｧ�ｽｸ郢ｧ雋槭�ｻ邵ｺ蜉ｱ窶ｻ邵ｺ荵晢ｽ臥ｹ晁ｼ斐≦郢晢ｽｼ郢晢ｽｫ郢晏ｳｨ竊楢ｬ鯉ｽｻ郢ｧ蛹ｺﾎｦ陞ｳ螢ｹﾂ繝ｻ""
    global mode, enemy_status
    mode = "field"

    if battle_window is not None:
        battle_window.show_message(message)
        # battle_window.opacity = 0

    enemy_status = None
    # TODO: 陷肴剌闌懆ｭ弱ｅ竊哲PC郢ｧ蜻茨ｽｶ蛹ｻ笘�邵ｲ竏壹�ｻ郢晢ｽｬ郢ｧ�ｽ､郢晢ｽ､郢晢ｽｼHP郢ｧ雋槫ｱ楢包ｽｩ邵ｺ蜷ｶ�ｽ狗ｸｲ竏壺�醍ｸｺ�ｽｩ邵ｺ�ｽｮ陷��ｽｦ騾�繝ｻ�ｽ堤ｸｺ阮呻ｼ�邵ｺ�ｽｫ陷茨ｽ･郢ｧ蠕娯ｻ郢ｧ繧��ｽ育ｸｺ繝ｻﾂ繝ｻ

def handle_battle_key(key: str):
    """郢晁�後Κ郢晢ｽｫ闕ｳ�ｽｭ邵ｺ�ｽｮ郢ｧ�ｽｭ郢晢ｽｼ陷茨ｽ･陷牙ｸ呻ｽ定怎�ｽｦ騾�繝ｻ笘�郢ｧ荵敖繧��ｽｻ鄙ｫ繝ｻ A郢ｧ�ｽｭ郢晢ｽｼ邵ｺ�ｽｧ隰ｾ�ｽｻ隰ｦ繝ｻ笆｡邵ｺ莉｣�ｽ定ｫ�ｽｳ陞ｳ螢ｹﾂ繝ｻ""
    global player_status, enemy_status

    if key.lower() != "a":
        return

    if player_status is None or enemy_status is None:
        return

    from battle_engine import player_attack, enemy_attack

    # 1) 郢晏干ﾎ樒ｹｧ�ｽ､郢晢ｽ､郢晢ｽｼ邵ｺ�ｽｮ隰ｾ�ｽｻ隰ｦ繝ｻ
    dmg = player_attack(player_status, enemy_status)
    if battle_window is not None:
        battle_window.update_status(player_status, enemy_status)
        battle_window.show_message(
            f"{player_status.name} 邵ｺ�ｽｮ邵ｺ阮吮鴬邵ｺ蛛ｵ窶ｳ繝ｻ繝ｻ{enemy_status.name} 邵ｺ�ｽｫ {dmg} 郢敖郢晢ｽ｡郢晢ｽｼ郢ｧ�ｽｸ繝ｻ繝ｻ
        )

    if enemy_status.is_dead():
        end_battle(f"{enemy_status.name} 郢ｧ繝ｻ邵ｺ貅倪凰邵ｺ蜉ｱ笳�繝ｻ繝ｻ)
        return

    # 2) 隰ｨ�ｽｵ邵ｺ�ｽｮ陷ｿ閧ｴ闌ｶ
    dmg2 = enemy_attack(enemy_status, player_status)
    if battle_window is not None:
        battle_window.update_status(player_status, enemy_status)
        battle_window.show_message(
            f"{enemy_status.name} 邵ｺ�ｽｮ邵ｺ阮吮鴬邵ｺ蛛ｵ窶ｳ繝ｻ繝ｻ{player_status.name} 邵ｺ�ｽｯ {dmg2} 郢敖郢晢ｽ｡郢晢ｽｼ郢ｧ�ｽｸ郢ｧ蛛ｵ竕ｧ邵ｺ莉｣笳�繝ｻ繝ｻ
        )

    if player_status.is_dead():
        end_battle("郢ｧ繝ｻ�ｽ臥ｹｧ蠕娯ｻ邵ｺ蜉ｱ竏ｪ邵ｺ�ｽ｣邵ｺ貅ｪﾂ�ｽｦ遯ｶ�ｽｦ")
        # TODO: 郢晏干ﾎ樒ｹｧ�ｽ､郢晢ｽ､郢晢ｽｼ邵ｺ�ｽｮHP郢晢ｽｪ郢ｧ�ｽｻ郢昴�ｻ繝ｨ郢ｧ繝ｻ�ｽｾ�ｽｩ雎｢�ｽｻ陷��ｽｦ騾�繝ｻ竊醍ｸｺ�ｽｩ郢ｧ蛛ｵ�ｼ�邵ｺ阮吶帝勗蠕娯鴬邵ｲ繝ｻ

def on_key_press(key: str):
    """陷茨ｽｨ闖ｴ阮吶�ｻ郢ｧ�ｽｭ郢晢ｽｼ陷茨ｽ･陷牙ｸ吶Ρ郢晢ｽｳ郢晏ｳｨﾎ帷ｸｲ繧�繝ｵ郢ｧ�ｽ｣郢晢ｽｼ郢晢ｽｫ郢晏ｳｨﾎ皮ｹ晢ｽｼ郢昴�ｻ郢晁�後Κ郢晢ｽｫ郢晢ｽ｢郢晢ｽｼ郢晏ｳｨ縲定怎�ｽｦ騾�繝ｻ�ｽ定崕繝ｻ�ｿ郢ｧ荵敖繝ｻ""
    if mode == "battle":
        handle_battle_key(key)
        return

    # mode == "field" 邵ｺ�ｽｮ邵ｺ�ｽｨ邵ｺ髦ｪ繝ｻ邵ｲ竏ｽ�ｽｻ鄙ｫ竏ｪ邵ｺ�ｽｧ鬨ｾ螢ｹ�ｽ顔ｸｺ�ｽｮ驕假ｽｻ陷崎ｼ披�醍ｸｺ�ｽｩ郢ｧ螳夲ｽ｡蠕娯鴬邵ｲ繝ｻ
    if key in ("up", "down", "left", "right"):
        # move_player(key)  # 隴鯉ｽ｢陝�蛟･繝ｻ驕假ｽｻ陷崎ｼ釆溽ｹｧ�ｽｸ郢昴�ｻ縺醍ｹｧ雋樔ｻ也ｸｺ�ｽｳ陷��ｽｺ邵ｺ繝ｻ
        return

    # 關謎ｹ昶斡邵ｺ�ｽｰ Day3 邵ｺ�ｽｮ邵ｲ蜷娜C邵ｺ�ｽｫ髫ｧ�ｽｱ邵ｺ蜉ｱﾂｰ邵ｺ莉｣�ｽ狗ｸｲ讎翫�ｻ騾�繝ｻ繝ｻ闕ｳﾂ鬩幢ｽｨ邵ｺ荵晢ｽ�
    # start_battle("slime") 郢ｧ雋樔ｻ也ｸｺ�ｽｶ邵ｺ�ｽｨ郢晁�後Κ郢晢ｽｫ邵ｺ�ｽｫ陷茨ｽ･郢ｧ蠕鯉ｽ狗ｹｧ�ｽ､郢晢ｽ｡郢晢ｽｼ郢ｧ�ｽｸ邵ｺ�ｽｧ邵ｺ蜷ｶﾂ繝ｻ

if __name__ == "__main__":
    print("Day4 騾包ｽｨ邵ｺ�ｽｮ main_day4.py 邵ｺ貅倪螺邵ｺ讎雁ｺ顔ｸｺ�ｽｧ邵ｺ蜷ｶﾂ繝ｻ)
    print("陞ｳ貅倥�ｻ郢晢ｽｭ郢ｧ�ｽｸ郢ｧ�ｽｧ郢ｧ�ｽｯ郢晏現繝ｻ App 郢ｧ�ｽｯ郢晢ｽｩ郢ｧ�ｽｹ邵ｺ�ｽｫ驍ｨ繝ｻ竏ｩ髴趣ｽｼ郢ｧ阮吶堤ｸｺ雍具ｽｽ�ｽｿ邵ｺ繝ｻ�ｿ･邵ｺ�｣ｰ邵ｺ霈費ｼ樒ｸｲ繝ｻ)
