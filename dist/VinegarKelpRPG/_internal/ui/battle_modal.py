from kivy.clock import Clock
from kivy.uix.modalview import ModalView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle


class BattleModal(ModalView):
    def __init__(self, player, enemy, controller, on_finish, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (1, 1)
        self.auto_dismiss = False

        self.player = player
        self.enemy = enemy
        self.controller = controller
        self.on_finish = on_finish

        # 終了時の結果を一時保持
        self._final_result = None

        layout = BoxLayout(orientation="vertical")

        self.info = Label(text=self._status_text())
        self.log = Label(text="戦闘開始！")

        attack_btn = Button(text="攻撃")
        attack_btn.bind(on_release=self.attack)

        layout.add_widget(self.info)
        layout.add_widget(self.log)
        layout.add_widget(attack_btn)

        self.add_widget(layout)

    def _status_text(self):
        return (
            f"{self.player.name} HP {self.player.hp}/{self.player.max_hp}\n"
            f"{self.enemy.name} HP {self.enemy.hp}/{self.enemy.max_hp}"
        )

    def attack(self, *args):
        result = self.controller.handle_attack()
        if result is None:
            return

        self.info.text = self._status_text()
        self.log.text = result["log"]

        if result["finished"]:
            self._final_result = result["result"]
            Clock.schedule_once(self._finish_after_delay, 1.0)

    def _finish_after_delay(self, dt):
        if self._final_result is not None:
            self.on_finish(self._final_result)
        self.dismiss()