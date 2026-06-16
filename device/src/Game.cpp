// Game.cpp — 情境物件實作（IMU 讀數、DEV 疊圖）。
#include "Game.h"
#include <M5Unified.h>
#include <cmath>
#include <cstdio>
#include "config.h"
#include "dev.h"

void Game::begin(M5Canvas* cv) {
    canvas = cv;
    assets.setCanvas(cv);
    assets.setCharacter(config::DEFAULT_CHARACTER);

    // 素材：開機從 LittleFS 分區載入 PSRAM，再注入 AssetManager。
    // 失敗（未燒素材分區 / 掛載失敗）→ 不注入，全程走佔位色塊，遊戲流程照常可測。
    if (assetStore.begin() && assetStore.load(config::DEFAULT_CHARACTER)) {
        assets.setImages(assetStore.images(), assetStore.count());
    } else {
        Serial.println("[Game] 素材不可用 → 佔位模式（請先 pio run -t uploadfs）");
    }

    // IMU：dev::SKIP_IMU 可強制停用；否則看 M5Unified 是否成功初始化內建 MPU6886。
    imuOk = !dev::SKIP_IMU && (M5.Imu.isEnabled());
}

ImuMotion Game::imuMotion() {
    if (!imuOk) return {false, 0.0f, 0.0f};
    float ax, ay, az, gx, gy, gz;
    if (!M5.Imu.getAccel(&ax, &ay, &az) || !M5.Imu.getGyro(&gx, &gy, &gz))
        return {false, 0.0f, 0.0f};
    float amag = std::sqrt(ax * ax + ay * ay + az * az);   // 靜止 ≈ 1.0
    float gmag = std::sqrt(gx * gx + gy * gy + gz * gz);   // 靜止 ≈ 3 (°/s)
    return {true, amag, gmag};
}

bool Game::isNight() {
    // Fire 無 RTC 晶片，原 Python 版此功能本就選用 → 維持回 false。
    return false;
}

void Game::drawDebugOverlay(StateId stateId) {
    Metrics& m = metrics;
    canvas->fillRect(0, 226, config::SCREEN_W, 14, rgb(0x101018));
    canvas->setFont(&fonts::Font0);
    canvas->setTextColor(config::GREEN);
    canvas->setTextDatum(textdatum_t::top_left);
    char buf[64];
    std::snprintf(buf, sizeof(buf), "DEV %s  G%d L%d E%d R%d%%",
                  stateName(stateId), (int)m.growth, (int)m.life, (int)m.sleep,
                  (int)m.rhythm_rate());
    canvas->drawString(buf, 4, 228);
}

void Game::drawBattery() {
    // 右上角電池圖示。M5.Power 讀數：level 0~100（-1 未知）、isCharging() 充電中。
    int level = M5.Power.getBatteryLevel();          // 0~100，未知回 -1
    bool charging = (M5.Power.isCharging() == m5::Power_Class::is_charging);

    // 幾何（右上角，留 4px 邊距）：本體 + 右側正極小凸點。
    constexpr int BW = 24, BH = 12, NUB_W = 2, NUB_H = 6;
    constexpr int PAD = 4;
    int x = config::SCREEN_W - PAD - NUB_W - BW;     // 本體左上 x
    int y = PAD;                                      // 本體左上 y

    // 未知電量：畫空殼 + 問號，不誤導。
    if (level < 0) {
        canvas->drawRect(x, y, BW, BH, config::BLACK);
        canvas->fillRect(x + BW, y + (BH - NUB_H) / 2, NUB_W, NUB_H, config::BLACK);
        canvas->setFont(&fonts::Font0);
        canvas->setTextColor(config::BLACK);
        canvas->setTextDatum(textdatum_t::middle_center);
        canvas->drawString("?", x + BW / 2, y + BH / 2);
        return;
    }
    if (level > 100) level = 100;

    // 依電量分色：>50 綠、>20 黃、其餘紅；充電中固定亮天藍。
    uint16_t fill = charging      ? config::ACCENT
                  : level > 50    ? config::GREEN
                  : level > 20    ? config::YELLOW
                                  : config::RED;

    // 外框（黑）＋右側凸點。
    canvas->drawRect(x, y, BW, BH, config::BLACK);
    canvas->fillRect(x + BW, y + (BH - NUB_H) / 2, NUB_W, NUB_H, config::BLACK);

    // 內部依百分比填色（內縮 2px 留白邊）。
    int innerW = BW - 4;
    int fillW = (innerW * level + 50) / 100;         // 四捨五入
    if (fillW > 0) canvas->fillRect(x + 2, y + 2, fillW, BH - 4, fill);

    // 充電中：本體上疊一個小閃電。
    if (charging) {
        int cx = x + BW / 2, cy = y + BH / 2;
        canvas->fillTriangle(cx + 1, cy - 4, cx - 3, cy + 1, cx,     cy + 1, config::WHITE);
        canvas->fillTriangle(cx,     cy - 1, cx + 3, cy - 1, cx - 1, cy + 4, config::WHITE);
    }

    // 百分比數字（電池左側，右對齊）。
    char buf[8];
    std::snprintf(buf, sizeof(buf), "%d%%", level);
    canvas->setFont(&fonts::Font0);
    canvas->setTextColor(config::BLACK);
    canvas->setTextDatum(textdatum_t::middle_right);
    canvas->drawString(buf, x - 3, y + BH / 2);
}

const char* stateName(StateId id) {
    switch (id) {
        case StateId::Init:       return "init";
        case StateId::NormalRoom: return "normal_room";
        case StateId::Feeding:    return "feeding";
        case StateId::Sleeping:   return "sleeping";
        case StateId::Petting:    return "petting";
        case StateId::Ending:     return "ending";
        default:                  return "none";
    }
}
