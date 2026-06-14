import base64, os

ASSETS = "/Users/norman/SideProject/HoloTamagotchi/web/demo-assets"

def uri(name):
    with open(os.path.join(ASSETS, name), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"

def img(name, w):
    return f"<img src='{uri(name)}' width='{w}'/>"

flow = f"""flowchart TD
    Start([🔌 開機 / 重新開始]) --> INIT

    INIT["{img('egg_03.png',84)}<br/><b>INIT 破蛋</b><br/>動畫 24f → metrics.reset()"]
    INIT --> NORMAL

    NORMAL["{img('idle_00.png',84)}<br/><b>NORMAL 日常</b><br/>每秒 tick：growth +0.0001<br/>life −0.0003 / sleep −0.02"]

    NORMAL -->|"按 B → FEED"| FEEDING
    NORMAL -->|"按 B → PET"| PETTING
    NORMAL -->|"sleep ≤ 10 或 idle ≥ 400f"| SLEEPING
    NORMAL -->|"life &lt; 0"| END_RUN
    NORMAL -->|"growth ≥ 100"| ENDCHK

    NORMAL -.->|"sleep &lt; 30, P=0.15"| YAWN["{img('yawn_00.png',72)}<br/>打哈欠"]
    NORMAL -.->|"P=0.10"| CHEER["{img('cheer_00.png',72)}<br/>歡呼"]
    YAWN -.-> NORMAL
    CHEER -.-> NORMAL

    FEEDING["{img('food_0_00.png',40)} {img('eat_00.png',72)}<br/><b>FEEDING 餵食</b><br/>選食物 → 進食<br/>life +18"]
    FEEDING --> NORMAL

    PETTING["{img('pet_00.png',72)} {img('emo_success_00.png',72)}<br/><b>PETTING 摸頭 8s</b><br/>A/C 交替撫摸<br/>strokes ≥ 28 → success"]
    PETTING --> NORMAL

    SLEEPING["{img('sleep_00.png',84)}<br/><b>SLEEPING 睡眠</b><br/>sleep +2/s，life 暫停"]
    SLEEPING -->|"按 C / 搖晃 &gt; 4.0<br/>或 sleep ≥ 100 自然醒"| NORMAL

    ENDCHK{{"結局分類<br/>互動率 rhythm_rate ?"}}
    ENDCHK -->|"&gt; 90%"| END_GOOD["{img('end_idol_00.png',84)}<br/><b>好結局 GOOD</b><br/>end_good"]
    ENDCHK -->|"30% ~ 90%"| END_NORMAL["{img('end_office_00.png',84)}<br/><b>普通結局 NORMAL</b><br/>end_normal"]
    ENDCHK -->|"&lt; 30%"| END_BAD["{img('end_pirate_00.png',84)}<br/><b>壞結局 BAD</b><br/>end_bad"]
    END_RUN["{img('end_runaway_00.png',84)}<br/><b>離家出走 RUN AWAY</b><br/>end_runaway"]

    END_GOOD --> RESTART([按任意鍵])
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

with open("/tmp/mermaid-flow.mmd", "w") as f:
    f.write(flow)
print("written", len(flow), "bytes")
