# Day1 生徒用ワークシート（Kivy/KivyMD）
## 到達（DoD）
- CSVタイル上でプレイヤ矩形が移動する（壁すり抜けOK）

## 手順
1. `pip install kivy kivymd` を実行
2. `python main_day1.py` で起動
3. 下記TODOから**1つ**実装：Shift走る／慣性／摩擦／Clamp

## ヒント
- Shift走る：Shiftキー（keycode 304/303）で `speed *= RUN_MULTIPLIER`
- 慣性/摩擦：`vx = vx*(1-ACCEL) + ax*speed*ACCEL` → `vx *= FRICTION`（vyも同様）
- Clamp：`px = max(0, min(px, map_w - w))`
