from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty


class MessageWindow(BoxLayout):
    # 画面下部にメッセージを表示するシンプルなウィンドウ
    text = StringProperty("")

    def show_message(self, text_list):
        # セリフのリストを受け取り、最初の1行だけ表示する簡易版。
        if not text_list:
            self.text = ""
            return
        self.text = text_list[0]
