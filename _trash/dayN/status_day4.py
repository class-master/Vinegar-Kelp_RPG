�ｻｿ# status_day4.py
# Day4 騾包ｽｨ繝ｻ螢ｹ繝ｻ郢晢ｽｬ郢ｧ�ｽ､郢晢ｽ､郢晢ｽｼ郢ｧ繝ｻ髮ｰ邵ｺ�ｽｮ郢ｧ�ｽｹ郢昴�ｻ繝ｻ郢ｧ�ｽｿ郢ｧ�ｽｹ郢ｧ蜻域｡ｶ邵ｺ繝ｻ縺醍ｹ晢ｽｩ郢ｧ�ｽｹ陞ｳ螟ゑｽｾ�ｽｩ邵ｲ繝ｻ

class Status:
    """郢晏干ﾎ樒ｹｧ�ｽ､郢晢ｽ､郢晢ｽｼ郢ｧ繝ｻ髮ｰ邵ｺ�ｽｮ郢ｧ�ｽｹ郢昴�ｻ繝ｻ郢ｧ�ｽｿ郢ｧ�ｽｹ郢ｧ螳夲ｽ｡�ｽｨ邵ｺ蜷ｶ縺咏ｹ晢ｽｳ郢晏干ﾎ晉ｸｺ�ｽｪ郢ｧ�ｽｯ郢晢ｽｩ郢ｧ�ｽｹ邵ｲ繝ｻ""

    def __init__(self, name, max_hp, attack, defense=0):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense

    def is_dead(self) -> bool:
        """HP邵ｺ繝ｻ闔会ｽ･闕ｳ荵昶�醍ｹｧ迚卍蛛ｵ�ｽ檎ｸｺ�ｽｦ邵ｺ繝ｻ�ｽ狗ｸｺ�ｽｨ邵ｺ�ｽｿ邵ｺ�ｽｪ邵ｺ蜷ｶﾂ繝ｻ""
        return self.hp <= 0

    def take_damage(self, amount: int) -> int:
        """郢敖郢晢ｽ｡郢晢ｽｼ郢ｧ�ｽｸ郢ｧ雋槫･ｳ邵ｺ莉｣窶ｻHP郢ｧ蜻茨ｽｸ蟶呻ｽ臥ｸｺ蜻ｻ�ｽｼ繝ｻ隴幢ｽｪ雋�ﾂ邵ｺ�ｽｫ邵ｺ�ｽｯ邵ｺ�ｽｪ郢ｧ蟲ｨ竊醍ｸｺ繝ｻ�ｽｼ蟲ｨﾂ繝ｻ""
        if amount < 0:
            amount = 0
        self.hp = max(self.hp - amount, 0)
        return self.hp
