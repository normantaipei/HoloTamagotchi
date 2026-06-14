import base64, os

ASSETS = "/Users/norman/SideProject/HoloTamagotchi/web/demo-assets"

def uri(name):
    with open(os.path.join(ASSETS, name), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"

def img(name, w):
    return f"<img src='{uri(name)}' width='{w}'/>"

# 角色下方文字標注沿用模擬器（web/utils/animations.ts ACTIONS / useI18n.ts）的標籤。
# L[語言][節點] = 該節點顯示文字
L = {
    "zh": {  # 模擬器中文：bilingual「中 EN」格式
        "start": "開始 / 重新開始", "restart": "重新開始",
        "egg": "破殼 Egg", "idle": "待機 Idle", "eat": "餵食 Eat",
        "pet": "摸頭 Pet", "sleep": "睡覺 Sleep",
        "yawn": "打哈欠 Yawn", "cheer": "加油 Cheer",
        "endchk": "結局 Ending", "good": "好結局 Good End",
        "normal": "普通結局 Normal End", "bad": "壞結局 Bad End",
        "runaway": "離家出走 Run Away",
        "e_feed": "餵食", "e_pet": "摸頭", "e_sleep": "想睡 / 太久沒互動",
        "e_grow": "長大了", "e_neglect": "太久沒照顧",
        "e_rand": "偶爾", "e_wake": "被叫醒 / 睡飽",
        "e_often": "常陪她", "e_soso": "普普通通", "e_rare": "很少陪",
    },
    "en": {  # 模擬器英文（useI18n.ts en）
        "start": "Start / Restart", "restart": "Restart",
        "egg": "Egg", "idle": "Idle", "eat": "Eat",
        "pet": "Pet", "sleep": "Sleep",
        "yawn": "Yawn", "cheer": "Cheer",
        "endchk": "Ending", "good": "Good End",
        "normal": "Normal End", "bad": "Bad End",
        "runaway": "Run Away",
        "e_feed": "Feed", "e_pet": "Pet", "e_sleep": "Sleepy / idle too long",
        "e_grow": "Grown up", "e_neglect": "Neglected too long",
        "e_rand": "sometimes", "e_wake": "Woken / rested",
        "e_often": "Often", "e_soso": "So-so", "e_rare": "Rarely",
    },
}


def build(t):
    return f"""flowchart TD
    Start([{t['start']}]) --> INIT

    INIT["{img('egg_03.png',96)}<br/><b>{t['egg']}</b>"]
    INIT --> NORMAL

    NORMAL["{img('idle_00.png',96)}<br/><b>{t['idle']}</b>"]

    NORMAL -->|"{t['e_feed']}"| FEEDING
    NORMAL -->|"{t['e_pet']}"| PETTING
    NORMAL -->|"{t['e_sleep']}"| SLEEPING
    NORMAL -->|"{t['e_grow']}"| ENDCHK
    NORMAL -->|"{t['e_neglect']}"| END_RUN

    NORMAL -.->|"{t['e_rand']}"| YAWN["{img('yawn_00.png',80)}<br/>{t['yawn']}"]
    NORMAL -.->|"{t['e_rand']}"| CHEER["{img('cheer_00.png',80)}<br/>{t['cheer']}"]
    YAWN -.-> NORMAL
    CHEER -.-> NORMAL

    FEEDING["{img('eat_00.png',96)}<br/><b>{t['eat']}</b>"]
    FEEDING --> NORMAL

    PETTING["{img('pet_00.png',96)}<br/><b>{t['pet']}</b>"]
    PETTING --> NORMAL

    SLEEPING["{img('sleep_00.png',96)}<br/><b>{t['sleep']}</b>"]
    SLEEPING -->|"{t['e_wake']}"| NORMAL

    ENDCHK{{"{t['endchk']}"}}
    ENDCHK -->|"{t['e_often']}"| END_GOOD["{img('end_idol_00.png',96)}<br/><b>{t['good']}</b>"]
    ENDCHK -->|"{t['e_soso']}"| END_NORMAL["{img('end_office_00.png',96)}<br/><b>{t['normal']}</b>"]
    ENDCHK -->|"{t['e_rare']}"| END_BAD["{img('end_pirate_00.png',96)}<br/><b>{t['bad']}</b>"]
    END_RUN["{img('end_runaway_00.png',96)}<br/><b>{t['runaway']}</b>"]

    END_GOOD --> RESTART([{t['restart']}])
    END_NORMAL --> RESTART
    END_BAD --> RESTART
    END_RUN --> RESTART
    RESTART --> INIT

    classDef normal fill:#eaf4ff,stroke:#3b82f6,stroke-width:2px;
    classDef sleep fill:#06141e,color:#fff,stroke:#1e3a5f;
    classDef ending fill:#fff7ed,stroke:#f59e0b;
    classDef event fill:#f0fdf4,stroke:#22c55e,stroke-dasharray:4 3;
    class NORMAL normal;
    class SLEEPING sleep;
    class END_GOOD,END_NORMAL,END_BAD,END_RUN,ENDCHK ending;
    class YAWN,CHEER event;
"""


for lang in ("zh", "en"):
    out = f"/tmp/mermaid-art-flow-{lang}.mmd"
    with open(out, "w") as f:
        f.write(build(L[lang]))
    print("written", lang, "->", out)
