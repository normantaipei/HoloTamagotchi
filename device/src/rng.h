// rng.h — 亂數（對應 Python 的 urandom.getrandbits / random）。
// 用 ESP32 硬體亂數，歸一化成 0~1 浮點。
#pragma once
#include <esp_random.h>

inline float rnd() { return (float)esp_random() / 4294967295.0f; }
