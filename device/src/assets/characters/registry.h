// registry.h — 角色註冊表。
// 新增角色：複製 marine/ 改新資料夾、改 character.h，再到這裡 include + 加一筆。
// AssetManager 只依賴 getCharacter()。
#pragma once
#include "marine/character.h"
#include <cstring>

namespace assets {

inline const Character* getCharacter(const char* id) {
    if (std::strcmp(id, "marine") == 0) return &marine::CHARACTER;
    return &marine::CHARACTER;   // 未知 id → 退回預設
}

}  // namespace assets
