// Stubs.h — POC 階段的最小狀態實作（交付物 2 再補完整邏輯）。
//
// Feeding / Sleeping / Petting：畫標題 + 提示，按鍵返回普通房間，讓狀態機轉場可跑。
// Ending：依 endingKind / rhythm_rate 算出結局類別並畫對應佔位圖，按任意鍵重新開始。
#pragma once
#include "State.h"

class Feeding : public State {
public:
    explicit Feeding(Game* g) : State(g) {}
    StateId update() override;
};

class Sleeping : public State {
public:
    explicit Sleeping(Game* g) : State(g) {}
    StateId update() override;
};

class Petting : public State {
public:
    explicit Petting(Game* g) : State(g) {}
    StateId update() override;
};

class Ending : public State {
public:
    explicit Ending(Game* g) : State(g) {}
    void    onEnter() override;
    StateId update()  override;
private:
    const char* key_   = "end_normal";
    const char* title_ = "NORMAL END";
};
