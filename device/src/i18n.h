// i18n.h — 多國語言字串。
//
// 用法：i18n::get("cheer_msg_01") → 依目前語言回字串；找不到鍵回鍵本身。
// 對應原 i18n.py + assets/strings/*。新增語言：在 .cpp 的表加一筆 + set_lang。
#pragma once

namespace i18n {

void        set_lang(const char* lang);
const char* get(const char* key);
const char* lang();

}  // namespace i18n
