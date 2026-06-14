// i18n.cpp — 字串表實作。
//
// en 表確保內建字型可顯示（POC）。zh_tw 備妥，M5GFX 載入 CJK 字型後即可切換
// （UIFlow1 做不到，這是 C++ 版的 bonus）。表用簡單線性查找——字串數量很小，夠快。
#include "i18n.h"
#include "config.h"
#include <cstring>

namespace i18n {

namespace {

struct Entry { const char* key; const char* val; };

// --- en（對應 assets/strings/en.py）---
const Entry EN[] = {
    {"cheer_msg_01", "Let's do our best today!"},
    {"cheer_msg_02", "Thanks for staying with me!"},
    {"yawn_msg_01",  "Mmm... I'm getting sleepy..."},
    {"btn_menu",     "MENU"},
    {"btn_select",   "OK"},
    {"btn_eat",      "EAT"},
};

// --- zh_tw（備妥；需 CJK 字型才能正確顯示）---
const Entry ZH_TW[] = {
    {"cheer_msg_01", "今天也一起加油吧！"},
    {"cheer_msg_02", "謝謝你一直陪著我！"},
    {"yawn_msg_01",  "嗯……有點睏了……"},
    {"btn_menu",     "選單"},
    {"btn_select",   "確認"},
    {"btn_eat",      "餵食"},
};

struct Table { const char* name; const Entry* entries; int count; };

const Table TABLES[] = {
    {"en",    EN,    (int)(sizeof(EN) / sizeof(EN[0]))},
    {"zh_tw", ZH_TW, (int)(sizeof(ZH_TW) / sizeof(ZH_TW[0]))},
};
constexpr int TABLE_COUNT = (int)(sizeof(TABLES) / sizeof(TABLES[0]));

const Table* find_table(const char* lang) {
    for (int i = 0; i < TABLE_COUNT; ++i) {
        if (strcmp(TABLES[i].name, lang) == 0) return &TABLES[i];
    }
    return nullptr;
}

const Table* g_table = &TABLES[0];  // 預設 en；set_lang 於 setup 套用 DEFAULT_LANG

}  // namespace

void set_lang(const char* lang) {
    const Table* t = find_table(lang);
    if (t) g_table = t;
}

const char* get(const char* key) {
    if (g_table) {
        for (int i = 0; i < g_table->count; ++i) {
            if (strcmp(g_table->entries[i].key, key) == 0) return g_table->entries[i].val;
        }
    }
    return key;  // 找不到回鍵本身（與 Python 行為一致）
}

const char* lang() { return g_table ? g_table->name : "en"; }

}  // namespace i18n
