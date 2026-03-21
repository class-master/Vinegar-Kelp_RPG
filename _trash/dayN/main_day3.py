�ｻｿ# Day3 騾包ｽｨ邵ｺ�ｽｮ隘搾ｽｷ陷崎ｼ斐○郢ｧ�ｽｯ郢晢ｽｪ郢晏干繝ｨ邵ｺ�ｽｮ邵ｺ貅倪螺邵ｺ讎雁ｺ顔ｸｲ繝ｻ
# 陞ｳ貊�蝨邵ｺ�ｽｮ郢晏干ﾎ溽ｹｧ�ｽｸ郢ｧ�ｽｧ郢ｧ�ｽｯ郢晏現繝ｻ Player / NPC / 郢晄ｧｭ繝｣郢晁挙�ｽｪ�ｽｭ邵ｺ�ｽｿ髴趣ｽｼ邵ｺ�ｽｿ / 騾包ｽｻ鬮ｱ�ｽ｢郢ｧ�ｽｯ郢晢ｽｩ郢ｧ�ｽｹ邵ｺ�ｽｮ陷ｷ讎顔√邵ｺ�ｽｫ
# 陷ｷ蛹ｻ�ｽ冗ｸｺ蟶吮ｻ隴厄ｽｸ邵ｺ閧ｴ驪､邵ｺ蛹ｻ窶ｻ邵ｺ荳岩味邵ｺ霈費ｼ樒ｸｲ繝ｻ

from typing import List

from entities_student import Player, NPC
from field.map_loader_kivy import load_map
from ui.message_window import MessageWindow
from systems.events.events_loader import load_events
from entities_student import is_adjacent

player = None
npcs: List[object] = []
events: dict = {}
message_window = None


def setup_game():
    # Day3 騾包ｽｨ邵ｺ�ｽｮ郢晁ｼ斐≦郢晢ｽｼ郢晢ｽｫ郢晏ｳｨ竊誰PC邵ｲ竏ｽ�ｽｼ螟奇ｽｩ�ｽｱ郢昴�ｻ繝ｻ郢ｧ�ｽｿ郢ｧ雋槭�ｻ隴帶ｺｷ蝟ｧ邵ｺ蜷ｶ�ｽ矩ｫ｢�ｽ｢隰ｨ�ｽｰ邵ｲ繝ｻ
    global player, npcs, events, message_window
    game_map = load_map('maps/village01.map')
    player = Player(x=5, y=5)
    npcs = [
        NPC('隴壼床�ｽｺ�ｽｺA', 8, 5, 'first_npc'),
        NPC('邵ｺ髮��ｽｺ蜉ｱ繝ｻ陝�繝ｻ, 10, 7, 'shop_girl'),
    ]
    events = load_events()
    message_window = MessageWindow()


def is_adjacent(player, npc) -> bool:
    dx = abs(player.x - npc.x)
    dy = abs(player.y - npc.y)
    return dx + dy == 1


def open_talk_window(event_id: str) -> None:
    if event_id not in events:
        print(f'[WARN] 隴幢ｽｪ騾具ｽｻ鬪ｭ�ｽｲ event_id: {event_id}')
        return
    lines = events[event_id]
    if message_window is not None:
        message_window.show_message(lines)
    else:
        print('[TALK]')
        for line in lines:
            print(' ', line)


def on_key_press(key: str) -> None:
    if key in ('up', 'down', 'left', 'right'):
        # move_player(key)  # 隴鯉ｽ｢陝�蛟･繝ｻ驕假ｽｻ陷崎ｼ釆溽ｹｧ�ｽｸ郢昴�ｻ縺醍ｸｺ�ｽｫ隶門玄�ｽｸ�ｽ｡邵ｺ蜉ｱ笘�郢ｧ繝ｻ
        return
    if key == 'e':
        for npc in npcs:
            if is_adjacent(player, npc):
                open_talk_window(npc.event_id)
                break


if __name__ == '__main__':
    print('Day3 騾包ｽｨ邵ｺ�ｽｮ main_day3.py 邵ｺ貅倪螺邵ｺ讎雁ｺ顔ｸｺ�ｽｧ邵ｺ蜷ｶﾂ繝ｻ)
    print('陞ｳ貅倥�ｻ郢晢ｽｭ郢ｧ�ｽｸ郢ｧ�ｽｧ郢ｧ�ｽｯ郢晏現繝ｻ App 郢ｧ�ｽｯ郢晢ｽｩ郢ｧ�ｽｹ邵ｺ�ｽｫ驍ｨ繝ｻ竏ｩ髴趣ｽｼ郢ｧ阮吶堤ｸｺ雍具ｽｽ�ｽｿ邵ｺ繝ｻ�ｿ･邵ｺ�｣ｰ邵ｺ霈費ｼ樒ｸｲ繝ｻ)
