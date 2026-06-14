// ui.cpp — UI 元件實作（對應 ui.py，箭頭 / 尾巴的逐列 fillRect 疊法照搬）。
#include "ui.h"
#include <M5Unified.h>
#include "config.h"
#include "i18n.h"

// 字型對應（UIFlow1 → M5GFX）：DefaultSmall→Font0、DejaVu18→Font2、DejaVu24→Font4。

// ─── ButtonHints ───
namespace { constexpr int HINT_CX[3] = {53, 160, 267}; constexpr int HINT_TOP = 216; }

void ButtonHints::draw(const Hint& a, const Hint& b, const Hint& c) {
    const Hint* slots[3] = {&a, &b, &c};
    for (int i = 0; i < 3; ++i) {
        const Hint& s = *slots[i];
        switch (s.kind) {
            case Hint::Text:   text(s.text, HINT_CX[i]); break;
            case Hint::ArrowL: arrow(HINT_CX[i], false);  break;
            case Hint::ArrowR: arrow(HINT_CX[i], true);   break;
            case Hint::None:   default: break;
        }
    }
}

void ButtonHints::text(const char* s, int cx) {
    canvas_->setFont(&fonts::Font0);
    canvas_->setTextColor(config::DARK);
    canvas_->setTextDatum(textdatum_t::top_left);
    int w = canvas_->textWidth(s);
    canvas_->drawString(s, cx - w / 2, HINT_TOP);
}

void ButtonHints::arrow(int cx, bool right) {
    int cy = HINT_TOP + 7;
    const int hr = 8, w = 12;                         // 半高、底寬
    for (int dy = -hr; dy <= hr; ++dy) {
        int span = (w * (hr - (dy < 0 ? -dy : dy))) / hr;   // 往尖端收斂
        if (span <= 0) continue;
        int x = right ? (cx - w / 2) : (cx - w / 2 + (w - span));
        canvas_->fillRect(x, cy + dy, span, 1, config::DARK);
    }
}

// ─── DialogBox ───
void DialogBox::show(const char* i18nKey) {
    const uint16_t BORDER = config::ACCENT;      // Cover 天藍框線
    const uint16_t FILL   = rgb(0x07304A);       // Cover 深藍底（白字可讀）
    canvas_->fillRoundRect(x_, y_, w_, h_, 10, BORDER);
    canvas_->fillRoundRect(x_ + 2, y_ + 2, w_ - 4, h_ - 4, 8, FILL);
    // 朝下小尾巴：一排遞減寬度的橫條堆成三角形（先寬天藍當框線，再窄深藍當內側）。
    int ty = y_ + h_;
    for (int i = 0; i < TAIL; ++i) {
        int hw = (TAIL - 2) - i;
        if (hw > 0) canvas_->fillRect(tailX_ - hw, ty + i, hw * 2, 1, BORDER);
        int hwi = (TAIL - 5) - i;
        if (hwi > 0) canvas_->fillRect(tailX_ - hwi, ty + i, hwi * 2, 1, FILL);
    }
    canvas_->setFont(&fonts::Font2);
    canvas_->setTextColor(config::WHITE);
    canvas_->setTextDatum(textdatum_t::top_left);
    canvas_->drawString(i18n::get(i18nKey), x_ + 12, y_ + 9);
}

// ─── Menu ───
void Menu::draw(int y) {
    int cw = config::SCREEN_W / count_;
    canvas_->setFont(&fonts::Font0);
    canvas_->setTextDatum(textdatum_t::top_left);
    for (int i = 0; i < count_; ++i) {
        int x = i * cw;
        bool sel = (i == idx_);
        uint16_t bg = sel ? config::PINK : config::DARK;
        int bx = x + 6, bw = cw - 12;
        canvas_->fillRoundRect(bx, y, bw, 40, 8, bg);
        canvas_->setTextColor(config::WHITE);
        int tw = canvas_->textWidth(labels_[i]);
        canvas_->drawString(labels_[i], bx + (bw - tw) / 2, y + (40 - 12) / 2);
    }
}
