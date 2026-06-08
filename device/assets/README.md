# assets/ — 美術與文案資源

這個資料夾放**所有非程式的素材**：角色圖片、動圖幀、字串文案。
程式邏輯完全不碰這裡的內容，靠 manifest（`characters/<id>/character.py`）對應，
所以「換圖 / 加角色 / 加語言」都不用改邏輯程式。

> 目前沒有任何圖片 → 螢幕上會顯示**色塊 + 方括號標籤**（例如 `[BG: Normal Room]`）。
> 那個標籤就是「這格要放什麼圖」的說明。把圖片放進對應資料夾、在 manifest 補上路徑後，
> 同一個位置就會自動換成圖片。

## 結構

```
assets/
├─ strings/                  # 多國語言文案（i18n）
│  ├─ zh_tw.py               #   繁中（需 CJK 字型才顯示，先備內容）
│  └─ en.py                  #   英文（螢幕預設）
└─ characters/
   └─ marine/                # 角色：寶鐘瑪琳（複製這層即可新增角色）
      ├─ character.py        #   manifest：色彩主題 / 佔位規格 / 圖片對應 / 對話
      ├─ backgrounds/        #   背景圖（bg_room, bg_game）320×240
      ├─ anim/               #   動作動圖幀（idle, yawn, cheer, eat, sleep, dance）
      ├─ portraits/          #   結局圖 + 音遊情緒圖（end_*, emo_*）
      └─ food/               #   甜點 5 種（food_0 ~ food_4）50×50
```

## 美術放圖流程

1. 把圖片（建議 `.jpg`，UIFlow1 `lcd.image` 支援；尺寸見下表）放進對應子資料夾。
2. 打開 `characters/marine/character.py`，在 `IMAGES` 把對應的 key 取消註解、填檔名：
   ```python
   IMAGES = {
       "bg_room": "backgrounds/room.jpg",
       "idle":    "anim/idle_00.jpg",
       "food_0":  "food/cake.jpg",
   }
   ```
3. 重跑程式，該位置就從色塊變成圖片。沒填到的 key 仍是色塊，可逐步替換。

## 需要的資源清單（key → 用途 / 建議尺寸）

| key | 資料夾 | 用途 | 尺寸 |
|-----|--------|------|------|
| `bg_room` / `bg_game` | backgrounds | 普通房間 / 遊戲房間背景 | 320×240 |
| `egg` | anim | 蛋裂開（初始化動畫） | ~70×90 |
| `idle` | anim | 待機 | ~80×74 |
| `yawn` / `cheer` / `eat` | anim | 打哈欠 / 加油 / 嚼食 | ~80×74 |
| `sleep` | anim | 蓋被子睡覺（2 幀） | ~100×70 |
| `dance` | anim | 唱跳（2~3 幀循環） | ~60×36 |
| `end_idol` / `end_office` / `end_pirate` / `end_runaway` | portraits | 4 種結局圖 | ~140×150 |
| `emo_s` / `emo_a` / `emo_c` / `emo_f` | portraits | 音遊結算 4 張情緒圖 | ~90×100 |
| `food_0` ~ `food_4` | food | 甜點 5 種 | 50×50 |

> 多幀動畫目前骨架是「同一張佔位輪播」。接圖時可在 manifest 與對應 state 擴成
> 多檔幀序（例如 `idle_00.jpg`/`idle_01.jpg`），這部分標記為 TODO。

## 新增角色

複製 `characters/marine/` → 改名，改 `character.py` 的 `NAME`/`THEME`/`IMAGES`，
最後在 `characters/__init__.py` 的 `REGISTRY` 註冊一行。把 `config.DEFAULT_CHARACTER`
指向新角色即可切換。
