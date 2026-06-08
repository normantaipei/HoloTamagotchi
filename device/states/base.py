# states/base.py — 狀態基底類別。
#
# 每個狀態實作三個鉤子：
#   on_enter() : 進入狀態時呼叫一次（畫靜態背景、初始化計時器…）
#   update()   : 每幀呼叫。回傳「下一個狀態 ID」以切換，回 None 表示停留。
#   on_exit()  : 離開狀態時呼叫一次（清理）。
#
# 狀態透過 self.game（Game 情境物件）取用硬體與子系統：
#   game.lcd / game.btnA/btnB/btnC / game.metrics / game.assets
#   game.is_night() / game.draw_metric_bars() / game.ending_kind


class State:
    def __init__(self, game):
        self.game = game

    def on_enter(self):
        pass

    def update(self):
        return None

    def on_exit(self):
        pass
