# dev.py — 開發用狀態覆寫（Dev State Override）
#
# 只在 config.DEV=True 時生效；prod 模式（DEV=False）完全略過、零開銷。
# 編輯 device/dev.json 即可快速 debug，不必苦等數值自然跑到特殊狀態：
#   - metrics      ：直接設定寵物核心數值，一開機就重現特定情境
#                    （sleep=5 馬上想睡 / growth=100 馬上結局 / life=-1 壞結局）
#   - start_state  ：強制起始狀態，跳過開場蛋動畫，直接進指定狀態
#                    （"init" / "normal_room" / "feeding" / "sleeping" /
#                     "mini_game" / "ending"）
#   - freeze_metrics：凍結數值（tick 不再自然增減），畫面停住方便觀察
#   - time_scale   ：自然數值倍速（如 60 → 1 秒當 1 分鐘跑），快速驗證自然轉場
#
# dev.json 不存在 / 格式錯誤 / 無 json 模組 → 靜默忽略，照正常流程跑。
# enabled=false 也可一鍵停用所有覆寫，不必刪檔。

import config

# 候選路徑：mount 開發時 cwd=device（"dev.json"）；燒錄到板上時可能在根目錄。
_PATHS = ("dev.json", "/dev.json", "/flash/dev.json")

# 可被覆寫的數值欄位（對應 Metrics 屬性）；值為 None / 缺鍵 = 不覆寫、用預設。
_METRIC_KEYS = ("growth", "life", "sleep",
                "total_interactions", "rhythm_plays", "rhythm_sa", "days")


def _load():
    if not config.DEV:
        return {}
    try:
        import json
    except ImportError:
        return {}
    for p in _PATHS:
        try:
            with open(p) as f:
                cfg = json.load(f)
        except OSError:
            continue                      # 此路徑無檔，換下一個候選
        except Exception as e:            # JSON 格式錯誤等：別讓開發檔搞掛遊戲
            print("[dev] dev.json parse error:", e)
            return {}
        if not cfg.get("enabled", True):
            return {}                     # 一鍵停用
        print("[dev] overrides loaded from", p)
        return cfg
    return {}


_CFG = _load()

# 一次性解析成模組常數，供熱路徑（tick）零成本讀取。
FREEZE     = bool(_CFG.get("freeze_metrics", False))
TIME_SCALE = float(_CFG.get("time_scale", 1.0) or 1.0)


def start_state():
    """回傳強制起始狀態 ID；未設定回 None（照正常 STATE_INIT 流程）。"""
    return _CFG.get("start_state") or None


def apply_metrics(m):
    """把 dev.json 的 metrics 覆寫套到 Metrics 物件上（在 reset() 末尾呼叫）。

    prod 模式或無覆寫時 _CFG 為空 → 直接 no-op，行為與原本完全相同。
    """
    over = _CFG.get("metrics") or {}
    for k in _METRIC_KEYS:
        v = over.get(k)
        if v is not None:
            setattr(m, k, v)
