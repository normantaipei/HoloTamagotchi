// dev.cpp — DEV 數值覆寫實作。
//
// POC：不覆寫任何數值（no-op），行為與正常 reset 完全相同。
// 要快速重現情境時，在這裡對 m 的欄位賦值即可，例如：
//   m.life = 5;            // 重現接近壞結局
//   m.growth = 99;         // 重現接近成長結局
#include "dev.h"
#include "Metrics.h"

void dev::applyMetrics(Metrics& m) {
    (void)m;
    // POC：無覆寫。
}
