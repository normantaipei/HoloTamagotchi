// ui.h — 共用 UI 元件：對話筐(DialogBox)、選單(Menu)、底部按鍵提示列(ButtonHints)。
//
// 對應原 ui.py。三者都是「畫面元件」，不持有遊戲狀態，由各 State 建立並驅動，
// 全部畫到傳入的 M5Canvas。
#pragma once
#include <cstdint>
#include <M5GFX.h>   // M5Canvas（LGFX_Sprite 別名，需完整定義）

// 底部三鍵提示列的一格內容：空 / 文字 / 左右箭頭。
struct Hint {
    // 無成員預設值 → 維持 aggregate，可用 Hint{kind, text} 初始化（gnu++11）。
    enum Kind { None, Text, ArrowL, ArrowR } kind;
    const char* text;
    static Hint none()              { return Hint{None, nullptr}; }
    static Hint txt(const char* s)  { return Hint{Text, s}; }
    static Hint arrowL()            { return Hint{ArrowL, nullptr}; }
    static Hint arrowR()            { return Hint{ArrowR, nullptr}; }
};

class ButtonHints {
public:
    explicit ButtonHints(M5Canvas* canvas) : canvas_(canvas) {}
    // 每格 a/b/c 對齊三顆實體鍵（A 左 / B 中 / C 右）。
    void draw(const Hint& a, const Hint& b, const Hint& c);
private:
    M5Canvas* canvas_;
    void text(const char* s, int cx);
    void arrow(int cx, bool right);
};

class DialogBox {
public:
    // 漫畫對話泡泡：圓角框 + 朝下小尾巴，浮在角色頭頂上方。
    DialogBox(M5Canvas* canvas, int x = 12, int y = 12, int w = 296, int h = 36, int tailX = 160)
        : canvas_(canvas), x_(x), y_(y), w_(w), h_(h), tailX_(tailX) {}
    void show(const char* i18nKey);   // 以 i18n key 傳入，自動取目前語言字串
private:
    M5Canvas* canvas_;
    int x_, y_, w_, h_, tailX_;
    static constexpr int TAIL = 12;
};

class Menu {
public:
    // labels：螢幕字串清單（指標陣列 + 數量）。
    Menu(M5Canvas* canvas, const char* const* labels, int count)
        : canvas_(canvas), labels_(labels), count_(count), idx_(0) {}
    void move(int d) { idx_ = ((idx_ + d) % count_ + count_) % count_; }
    int  selected() const { return idx_; }
    void draw(int y = 140);
private:
    M5Canvas* canvas_;
    const char* const* labels_;
    int count_;
    int idx_;
};
