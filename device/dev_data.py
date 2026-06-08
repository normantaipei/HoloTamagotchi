# dev_data.py — DEV 覆寫設定（取代舊的 dev.json）
#
# 為何用 .py 而非 .json：在 mpremote mount 開發下，模組 import 完之後再用 open() 讀
# 資料檔（dev.json）會卡死 mount 的序列協定 → 開機永遠停在讀檔、螢幕全黑。改成
# Python 模組、走 import 載入即可完全避開（import over mount 一切正常）。
#
# 用法：直接改下面的 CONFIG，存檔後重跑 `mpremote ... mount device run device/main.py`
# 即生效，免燒錄。值為 None = 不覆寫，用程式預設。enabled=False 可一鍵停用所有覆寫。
#
# 欄位：
#   start_state    強制起始狀態，跳過開場蛋動畫直接進指定狀態
#                  ("init" / "normal_room" / "feeding" / "sleeping" / "mini_game" / "ending")
#   skip_imu       跳過 IMU 初始化（mount 開發 / 無此硬體時設 True，搖一搖靜默停用）
#   freeze_metrics 凍結數值（tick 不再自然增減），畫面停住方便觀察
#   time_scale     自然數值倍速（如 60 → 1 秒當 1 分鐘跑），快速驗證自然轉場
#   metrics        直接設定寵物核心數值，一開機就重現特定情境
#                  （sleep=5 馬上想睡 / growth=100 馬上結局 / life=-1 壞結局）

CONFIG = {
    "enabled": True,
    "start_state": "normal_room",
    "skip_imu": True,
    "freeze_metrics": False,
    "time_scale": 1.0,
    "metrics": {
        "growth": None,
        "life": None,
        "sleep": None,
        "total_interactions": None,
        "rhythm_plays": None,
        "rhythm_sa": None,
        "days": None,
    },
}
