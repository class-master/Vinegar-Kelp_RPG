# P-RPG 統合版（バトル完全版）

このフォルダは、元の `class-master/P-RPG-provisional-`（ZIP受領版）に、
このスレッドで作成したバトル関連の変更を**1つに統合**したものです。

## 何が入った？
### 更新
- `battle_engine.py`
  - Day4互換（`calc_damage` / `player_attack` / `enemy_attack`）はそのまま維持
  - 追加API：`attack()`（会心/ブレ/ミスの“味付け”をまとめて扱える）

- `input/enemies_day4.json`
  - 既存の `slime` / `goblin` に加えて、`bat` / `wolf` / `knight` を追加

### 追加
- `battle_controller.py`
  - 戦闘の責務を「戦闘だけ」に閉じ込めるコントローラ
  - フィールド側は **開始/キー入力/結果受け取り** だけで結合できる
  - 入力：A=攻撃、D=防御
  - 防御：次の敵攻撃を軽減（1回）
  - AIっぽさ（軽量）：
    - A連打が続く → 敵が「ため」を混ぜる（次ターン強攻撃）
    - D連打が続く → 敵が「ガード崩し」を混ぜる（守りすぎは危険）

## フィールド側との“約束”（責任分離）
### フィールド（main）責務
- エンカウント条件を決める（歩数/タイル/乱数など）
- `BattleController.start(enemy_id)` を呼ぶ
- 戦闘中だけ `BattleController.handle_key(key)` に入力を流す
- `is_active` と `last_result` を見て復帰処理を行う

### 戦闘（battle）責務
- ターン進行、ダメージ計算、UI更新、勝敗判定
- 勝敗確定後に `BattleResult` を保持（`last_result`）

## 注意（グレーになりやすい点）
- `BattleController` は `battle_window` を渡されればUI更新しますが、
  **どの親Widgetに add/remove するか**は画面構造依存です。
  （実装は `battle_window` の生成/配置をフィールド側で行い、controllerへ渡すのが安全）

