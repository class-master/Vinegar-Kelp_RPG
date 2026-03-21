# controller.py
# プレイヤーの入力（キーボード操作）とキャラクターの挙動を制御するモジュールです。

class PlayerController:
    """
    プレイヤーの入力を受け取り、移動やアクション（決定キーなど）を制御します。
    """
    def __init__(self, player_entity, game_instance):
        self.player = player_entity
        self.game = game_instance
        # 押されているキーの状態を管理します
        self.active_keys = set()

    def update(self, dt):
        """
        毎フレーム呼び出され、キーの状態に応じてプレイヤーを動かします。
        """
        # バトル中などは移動を制限しますわ
        if self.game.mode != "field":
            return

        # キー入力に応じた移動量の計算
        dx, dy = 0, 0
        # Kivyのキーコード（環境に合わせて調整してくださいね）
        # 276=Left, 275=Right, 273=Up, 274=Down
        if 276 in self.active_keys: dx -= 1
        if 275 in self.active_keys: dx += 1
        if 273 in self.active_keys: dy += 1 # Kivyは上がプラス
        if 274 in self.active_keys: dy -= 1

        # 斜め移動の速度調整や、衝突判定をここから呼び出します
        if dx != 0 or dy != 0:
            self.move_player(dx, dy)

    def move_player(self, dx, dy):
        """
        衝突判定を確認した上で、プレイヤーの位置を更新します。
        """
        speed = self.game.player_speed
        new_x = self.player.px + dx * speed
        new_y = self.player.py + dy * speed

        # rect_collides（main.py等にある判定関数）を使って安全を確認しますわ
        from main import rect_collides
        if not rect_collides(new_x, self.player.py, self.player.w, self.player.h, self.game.grid):
            self.player.px = new_x
        if not rect_collides(self.player.px, new_y, self.player.w, self.player.h, self.game.grid):
            self.player.py = new_y

    def handle_action(self):
        """
        'E'キーなどが押された時の「調べる」動作を制御します。
        """
        # 前方の座標を計算して、イベントがないか確認します
        # event_manager.get_event(...) を呼び出すロジックですわね
        pass