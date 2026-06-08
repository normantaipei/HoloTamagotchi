# dev.py — 開發用狀態覆寫（Dev State Override）
#
# 只在 config.DEV=True 時生效；prod 模式（DEV=False）完全略過、零開銷。
# 編輯 device/dev_data.py 的 CONFIG 即可快速 debug，不必苦等數值自然跑到特殊狀態。
# 欄位說明見 dev_data.py。enabled=False 可一鍵停用所有覆寫，不必刪檔。
#
# 為何設定來源是 dev_data.py（Python 模組）而非 dev.json：mpremote mount 下，import
# 完模組後再 open() 讀資料檔會卡死 mount 協定（開機黑屏元兇）。改走 import 載入即可
# 避開——import over mount 一切正常。詳見 init() / dev_data.py 註解。

import config

# 可被覆寫的數值欄位（對應 Metrics 屬性）；值為 None / 缺鍵 = 不覆寫、用預設。
_METRIC_KEYS = ("growth", "life", "sleep",
                "total_interactions", "rhythm_plays", "rhythm_sa", "days")


def _load():
    if not config.DEV:
        return {}
    try:
        from dev_data import CONFIG     # 走 import 載入（mount 下安全；避開 open() 卡死）
    except ImportError:
        return {}                       # 無 dev_data.py → 照正常流程，零覆寫
    cfg = dict(CONFIG)
    if not cfg.get("enabled", True):
        return {}                       # 一鍵停用
    return cfg


# init() 前的安全預設值；實際值在 init() 載入 dev.json 後覆寫。
# 熱路徑（tick）讀 FREEZE / TIME_SCALE 仍是零成本的模組屬性存取。
_CFG       = {}
_LOADED    = False
FREEZE     = False
TIME_SCALE = 1.0
# 跳過 IMU 初始化。某些開機情境（韌體 launcher 佔住 I²C、mpremote 暖 reset）下，
# IMU() 建構會卡在 I²C 讀取而 block 整個開機。dev.json skip_imu=true 可略過（搖一搖停用）。
SKIP_IMU   = False


def init():
    """載入 dev.json 並解析成模組常數；冪等，只實際載入一次。

    為何「不」在 import 時做（這正是螢幕全黑的元兇）：mpremote mount 是序列線上的
    請求/回應協定，不容巢狀的檔案存取。dev 會被 metrics.py 在 main.py 頂層 import 時
    連帶 import；若在「dev.py 正透過 mount 被讀取中」又去載入設定（早期版用 open()
    讀 dev.json，現用 import dev_data），都會觸發巢狀 mount 讀取而死鎖——開機卡在
    import dev、永遠跑不到畫面。故把設定載入延到所有 import 完成後，由 main() 啟動時
    呼叫一次（此時 mount 閒置）。start_state() / apply_metrics() 也會自呼叫，漏叫也安全。
    """
    global _CFG, _LOADED, FREEZE, TIME_SCALE, SKIP_IMU
    if _LOADED:
        return
    _LOADED = True
    _CFG = _load()
    FREEZE     = bool(_CFG.get("freeze_metrics", False))
    TIME_SCALE = float(_CFG.get("time_scale", 1.0) or 1.0)
    SKIP_IMU   = bool(_CFG.get("skip_imu", False))


def start_state():
    """回傳強制起始狀態 ID；未設定回 None（照正常 STATE_INIT 流程）。"""
    init()
    return _CFG.get("start_state") or None


def apply_metrics(m):
    """把 dev.json 的 metrics 覆寫套到 Metrics 物件上（在 reset() 末尾呼叫）。

    prod 模式或無覆寫時 _CFG 為空 → 直接 no-op，行為與原本完全相同。
    """
    init()
    over = _CFG.get("metrics") or {}
    for k in _METRIC_KEYS:
        v = over.get(k)
        if v is not None:
            setattr(m, k, v)
