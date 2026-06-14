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
