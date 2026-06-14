// main.cpp — HoloTamagotchi 進入點（M5Stack Fire / Arduino C++ / M5Unified）。
//
// 由 UIFlow1 MicroPython 遷移而來。核心變更：全螢幕 M5Canvas 雙緩衝——
//   每幀各 State 把整張畫面畫進 PSRAM 的 canvas（off-screen），主迴圈最後一次
//   canvas.pushSprite() 貼到面板。根治原本 lcd.image 逐列更新（掃描線）的問題，
//   同時移除所有「只重畫變動區塊」的防閃爍簿記。
//
// 架構（對應原 Python 模組）：
//   config.h        全域設定        Metrics         核心數值
//   i18n            多語字串         AssetManager    資源（有圖畫圖、無圖佔位）
//   ui              共用 UI 元件     states/         狀態機（一狀態一類）
//   Game            共用情境物件     dev.h           DEV 覆寫
//
// 按鍵：A / B / C（各狀態內定義；普通房間 C=選單，選單內 A/C 移動、B 確認）。
#include <M5Unified.h>
#include "config.h"
#include "dev.h"
#include "i18n.h"
#include "Game.h"
#include "states/State.h"
#include "states/InitState.h"
#include "states/NormalRoom.h"
#include "states/Feeding.h"
#include "states/Sleeping.h"
#include "states/Petting.h"
#include "states/Ending.h"

// 全螢幕雙緩衝畫布（150KB，建在 PSRAM）。
static M5Canvas canvas(&M5.Display);

static Game game;

// 狀態查表：以 (int)StateId 索引。索引 0（None）不使用。
static State*  states[7] = {nullptr};
static StateId currentId = StateId::Init;
static State*  current   = nullptr;

void setup() {
    auto cfg = M5.config();
    cfg.internal_imu = true;        // 啟用內建 MPU6886（搖一搖 / 動作偵測）
    M5.begin(cfg);
    Serial.begin(115200);           // 序列除錯（對應原 Python 的 print）

    // 靜音喇叭，消除 DAC 底噪（對應原 mute_speaker）。
    M5.Speaker.setVolume(0);
    M5.Speaker.stop();

    i18n::set_lang(config::DEFAULT_LANG);

    // 建立 canvas（PSRAM）。Fire 有 4MB PSRAM，足以容納 320x240x16bpp。
    canvas.setColorDepth(16);
    // 全螢幕 16bpp canvas = 150KB；內部 SRAM 最大連續區塊僅 ~110KB 容不下，故放 PSRAM。
    canvas.setPsram(true);
    // 我們的圖片陣列是「原生位元組順序」的 RGB565（build_assets.py 產生），
    // 而 M5GFX pushImage 預設把影像資料當成 swapped；不開這個就會顏色暖↔冷反轉
    // （看起來像負片）。開了之後 pushImage 才會正確解讀我們的資料。
    canvas.setSwapBytes(true);
    if (!canvas.createSprite(config::SCREEN_W, config::SCREEN_H)) {
        // 萬一 PSRAM 配置失敗：面板直接報錯，方便上板診斷。
        M5.Display.fillScreen(TFT_RED);
        M5.Display.setCursor(8, 8);
        M5.Display.print("canvas alloc failed");
        while (true) delay(1000);
    }

    game.begin(&canvas);

    // 建立各狀態（canvas 已就緒）。
    states[(int)StateId::Init]       = new InitState(&game);
    states[(int)StateId::NormalRoom] = new NormalRoom(&game);
    states[(int)StateId::Feeding]    = new Feeding(&game);
    states[(int)StateId::Sleeping]   = new Sleeping(&game);
    states[(int)StateId::Petting]    = new Petting(&game);
    states[(int)StateId::Ending]     = new Ending(&game);

    // DEV：dev::START_STATE 可強制起始狀態，跳過開場直接除錯。
    currentId = (dev::START_STATE != StateId::None) ? dev::START_STATE : StateId::Init;
    current = states[(int)currentId];
    current->onEnter();
    Serial.printf("HoloTamagotchi started @ %s\n", stateName(currentId));
}

void loop() {
    static int stateFrame = 0;              // 本狀態已過幀數（切換時歸零）；驅動多幀素材輪播
    uint32_t t0 = millis();                 // 幀率對齊：量測本幀工作耗時

    M5.update();                            // 更新按鍵 / 觸控狀態（每圈一次）

    game.assets.setFrame(stateFrame);       // 多幀素材依此輪播（對應 web renderer.frame）
    StateId nxt = current->update();        // 邏輯 + 把整張畫面畫進 canvas

    if (config::DEV) game.drawDebugOverlay(currentId);

    canvas.pushSprite(0, 0);                // 一次貼到面板（無掃描線）

    if (nxt != StateId::None && nxt != currentId) {
        current->onExit();
        currentId = nxt;
        current = states[(int)currentId];
        current->onEnter();
        stateFrame = 0;                     // 新狀態從第 0 幀開始（與 web 每動作重置一致）
        Serial.printf("-> state %s\n", stateName(currentId));
    } else {
        stateFrame++;
    }

    // 幀率對齊：補足到 FRAME_MS（含繪圖 + pushSprite 耗時），固定步調、與 web 模擬器一致。
    // （原本「無條件 delay(FRAME_MS)」= 工作 + 50ms，會明顯偏慢。）
    uint32_t elapsed = millis() - t0;
    if (elapsed < (uint32_t)config::FRAME_MS) delay(config::FRAME_MS - elapsed);
}
