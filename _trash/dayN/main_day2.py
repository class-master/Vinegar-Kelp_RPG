�ｻｿ# -*- coding: utf-8 -*-
"""
RPG Rustic Master B 遯ｶ繝ｻDay2繝ｻ閧ｲ蜃ｽ陟募､逡代�ｻ蜊ｯivy
陋ｻ�ｽｰ鬩戊ｲｻ�ｽｼ螢ｼ�ｽ｣竏ｬ�ｽ｡譎会ｽｪ繝ｻ�ｽｼ諡ｾ邵ｺ�ｽｧ騾ｵ蛹ｺ謾ｸ郢ｧ螳夲ｽｪ�ｽｭ郢ｧﾂ繝ｻ莠包ｽｼ螟奇ｽｩ�ｽｱ郢敖郢晄ｺ倥�ｻ繝ｻ繝ｻ
騾具ｽｺ陞ｻ蛹��ｽｼ螟仙ｵｯ邵ｺ�ｽｨ隰�莨夲ｽｼ繝ｻlag邵ｺ�ｽｧ鬮｢遏ｩ蜩ｩ繝ｻ莨夲ｽｼ荳橸ｽｮ譎会ｽｮ�ｽｱ繝ｻ莠･蜿呵募干縲辿UD繝ｻ繝ｻ
"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Translate
from kivy.uix.label import Label
from kivy.properties import ListProperty
from config import WIDTH, HEIGHT, TILE_SIZE, MAP_CSV, PLAYER_SPEED, BG
from field.map_loader_kivy import load_csv_as_tilemap, load_tileset_regions

def rect_collides(px, py, w, h, grid, solid={1,2,3,4}): # 遶翫�ｻsolid陟大｢鍋�夂ｸｺ�ｽｨ陞｢竏壹■郢ｧ�ｽ､郢晢ｽｫID郢ｧ螳夲ｽｿ�ｽｽ陷会｣ｰ
    ts = TILE_SIZE
    min_c = max(0, int(px)//ts)
    max_c = min(len(grid[0])-1, int((px+w-1))//ts)
    min_r = max(0, int(py)//ts)
    max_r = min(len(grid)-1, int((py+h-1))//ts)
    for r in range(min_r, max_r+1):
        for c in range(min_c, max_c+1):
            if grid[r][c] in solid: # 遶翫�ｻ郢ｧ�ｽｿ郢ｧ�ｽ､郢晢ｽｫID邵ｺ謔滂ｽ｣竏墅懃ｹｧ�ｽｹ郢晏現竊鍋ｸｺ繧��ｽ狗ｸｺ荵昴Γ郢ｧ�ｽｧ郢昴�ｻ縺�
                wx, wy = c*ts, r*ts
                if not (px+w<=wx or wx+ts<=px or py+h<=wy or wy+ts<=py):
                    return True
    return False

class Game(Widget):
    cam=ListProperty([0,0])

    def __init__(self, **kw):
        super().__init__(**kw)
        self.size=(WIDTH,HEIGHT)
        self.grid,self.rows,self.cols = load_csv_as_tilemap(MAP_CSV)
        self.tiles = load_tileset_regions()
        ts=TILE_SIZE
        self.px=ts*3; self.py=ts*3; self.w=ts-6; self.h=ts-6
        self.keys=set()
        self.sign = (ts*10, ts*6, ts, ts)  # 騾ｵ蛹ｺ謾ｸ邵ｺ�ｽｮ闖ｴ蜥ｲ�ｽｽ�ｽｮ郢ｧ螳夲ｽｨ�ｽｭ陞ｳ繝ｻ
        self.msg = Label(text="驕擾ｽ｢陷奇ｽｰ郢ｧ�ｽｭ郢晢ｽｼ邵ｺ�ｽｧ驕假ｽｻ陷阪�ｻ E: 騾ｵ蛹ｺ謾ｸ郢ｧ螳夲ｽｪ�ｽｭ郢ｧﾂ", pos=(12,HEIGHT-28)) # HUD郢晢ｽ｡郢昴�ｻ縺晉ｹ晢ｽｼ郢ｧ�ｽｸ郢ｧ螳夲ｽｨ�ｽｭ陞ｳ繝ｻ
        self.add_widget(self.msg)

        Window.bind(on_key_down=self._kd, on_key_up=self._ku)
        Clock.schedule_interval(self.update, 1/60)
        
        self.cam = [0, 0]
    def _kd(self,win,key,*a):
        self.keys.add(key); return True

    def _ku(self,win,key,*a):
        self.keys.discard(key); return True

    def update(self,dt):
        left=276; right=275; up=274; down=273; ekey=101
        ax=(1 if right in self.keys else 0)-(1 if left in self.keys else 0)
        ay=(1 if down  in self.keys else 0)-(1 if up   in self.keys else 0)
        spd=PLAYER_SPEED
        nx=self.px+ax*spd
        if not rect_collides(nx, self.py, self.w, self.h, self.grid): self.px=nx
        ny=self.py+ay*spd
        if not rect_collides(self.px, ny, self.w, self.h, self.grid): self.py=ny
        
        # 騾ｵ蛹ｺ謾ｸ
        sx,sy,sw,sh=self.sign
        is_colliding_with_sign = not (self.px+self.w<=sx or sx+sw<=self.px or self.py+self.h<=sy or sy+sh<=self.py)
        if ekey in self.keys and is_colliding_with_sign:
            self.msg.text="邵ｲ蜊�諱夊ｭ夲ｽｿ邵ｲ莉｣�ｽ育ｸｺ繝ｻ�ｼ�邵ｺ譏ｴﾂ繝ｽustic隴壻ｻ｣竏医�ｻ繝ｻ
        else:
            self.msg.text="驕擾ｽ｢陷奇ｽｰ郢ｧ�ｽｭ郢晢ｽｼ邵ｺ�ｽｧ驕假ｽｻ陷阪�ｻ E: 騾ｵ蛹ｺ謾ｸ郢ｧ螳夲ｽｪ�ｽｭ郢ｧﾂ"
        
        self.cam[0]=max(0,self.px-self.width/2); self.cam[1]=max(0,self.py-self.height/2)
        self.draw()
        
    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(*BG); Rectangle(pos=self.pos,size=self.size)
            PushMatrix(); Translate(-self.cam[0],-self.cam[1],0)
            ts=TILE_SIZE
            for r,row in enumerate(self.grid):
                for c,tid in enumerate(row):
                    Rectangle(texture=self.tiles[tid], pos=(c*ts,r*ts), size=(ts,ts))
            # 騾ｵ蛹ｺ謾ｸ
            Color(0.8,0.6,0.25,1); Rectangle(pos=(self.sign[0],self.sign[1]), size=(self.sign[2],self.sign[3]))
            # 郢晏干ﾎ樒ｹｧ�ｽ､郢晢ｽ､
            Color(0.35,0.67,1,1); Rectangle(pos=(self.px,self.py), size=(self.w,self.h))
            PopMatrix()
class Day2(App):
    def build(self): return Game()
if __name__=="__main__": Day2().run()

#騾ｵ蛹ｺ謾ｸ邵ｺ�ｽｮ隴√�ｻ�ｽｭ蜉ｱ繝ｻ髯ｦ�ｽｨ驕会ｽｺ邵ｺ蠕後堤ｸｺ髦ｪ竊醍ｸｺ荵昶夢邵ｺ貅伉
