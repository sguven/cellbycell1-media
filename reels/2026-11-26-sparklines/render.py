"""Reel: A chart in every cell (sparklines).

Google Sheets (Docs Editors Help 3093289, SPARKLINE): SPARKLINE(data, [options]); default chart type is "line";
options as {"name","value";...}; "color" sets the line color for line charts, e.g. {"color","red"}. (The separate "sparkline chart" type in the chart
editor is retired; the SPARKLINE *function* is still documented.)
Excel (Microsoft Support "Use sparklines to show data trends": Microsoft 365, 2024, 2021, 2019, 2016; "Create
sparklines in Excel for Mac": 365/2024/2021 for Mac): select a blank cell, Insert > Sparklines > Line (or Column),
select the data cells, OK, then drag the handle down for the other rows. In Excel it is a menu feature, not a formula.
Every sparkline is drawn from the table values below; the "slipping" row is computed (strictly falling Jan->May).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> sparklines.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "sparklines"
DATE = "2026-11-26"

HDR = ["Rep", "Jan", "Feb", "Mar", "Apr", "May", "Trend"]
VALS = {"Ava": [420, 460, 510, 560, 610], "Noah": [640, 590, 530, 470, 410], "Mia": [380, 520, 340, 560, 450],
        "Leo": [500, 510, 495, 505, 515], "Zoe": [300, 360, 430, 390, 480]}
NAMES = list(VALS)
DATA = [HDR] + [[n] + [str(v) for v in VALS[n]] + [""] for n in NAMES]
SLIP = [i for i, n in enumerate(NAMES) if all(b < a for a, b in zip(VALS[n], VALS[n][1:]))]
assert SLIP == [1], SLIP            # only Noah falls every month
CW = [150, 112, 112, 112, 112, 112, 230]
LINE = (52, 120, 220)
RED_T = (253, 222, 223)

def make_sheet(y, row_h=92):
    s = Sheet(0, y, CW, DATA, row_h=row_h)
    s.x = (W - s.width()) // 2
    return s

def sparks(base, s, t, t0, kind="line", stagger=0.12, dur=0.6, col=LINE):
    for r in range(1, len(DATA)):
        a0 = t0 + (r - 1) * stagger
        cell_sparkline(base, s.cell_box(r, 6), VALS[NAMES[r - 1]], ease(seg(t, a0, a0 + dur)), kind=kind, col=col)

# ---------- hook ----------
L1, L2 = "A CHART IN", "EVERY CELL"
HF = fit_font("Bold", max(L1, L2, key=lambda x: F("Bold", 100).getlength(x)), 880, 190)

def sc_hook(t, D):
    base = background()
    pop_text(base, L1, W / 2, 400, HF, AMBER, t, -0.3, stroke=10)
    pop_text(base, L2, W / 2, 580, HF, AMBER, t, -0.2, stroke=10)
    s = make_sheet(760)
    s.draw(base, font_size=34, fills={(r, 6): (255, 243, 214) for r in range(1, 6)})
    sparks(base, s, t, -0.15, stagger=0.1, dur=0.55)
    s.outline(base, s.col_box(6), AMBER, width=7)
    d = ImageDraw.Draw(base)
    pa = ease(seg(t, 0.4, 0.65))
    if pa > 0: pill(d, W / 2, s.y + s.height() + 95, "1 FORMULA  ·  0 CHARTS", GREEN, size=44, a=pa)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, 0.4, 0.2, 10)

# ---------- problem ----------
def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "WALL OF NUMBERS", RED, "Who's slipping?", y=290)
    s = make_sheet(620 + int(20 * (1 - ease(seg(t, 0, 0.4)))))
    s.draw(base, font_size=34)
    for r in range(1, 6):
        b = s.cell_box(r, 6)
        pop_text(base, "?", (b[0] + b[2]) / 2, (b[1] + b[3]) / 2, F("Bold", 60), RED, t, 0.5 + 0.12 * r, stroke=6)
    return shake(base, t, 1.2, 0.25, 12)

# ---------- Google Sheets: result first, then the formula ----------
FX1 = "=SPARKLINE(B2:F2)"
def sc_sheets(t, D):
    base = background()
    label_card(base, t, 0.0, "GOOGLE SHEETS", BLUE, "Type one formula", y=280)
    s = make_sheet(580)
    rf = {}
    if t > 1.75: rf = {(SLIP[0] + 1, c): RED_T for c in range(7)}
    s.draw(base, font_size=34, fills=rf)
    sparks(base, s, t, 0.25)
    if t > 1.75:
        a = ease(seg(t, 1.75, 2.0))
        s.outline(base, [s.x, s.cell_box(SLIP[0] + 1, 0)[1], s.x + s.width(), s.cell_box(SLIP[0] + 1, 0)[3]], RED, a=a, width=7)
    formula_bar(base, 90, 1230, W - 180, FX1, t=t, t0=0.9, cps=30, colors=[("B2:F2", (200, 130, 0))], size=52)
    return shake(base, t, 1.75, 0.2, 10)

FX2 = '=SPARKLINE(B3:F3,{"color","red"})'
def sc_color(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Flag it in red", y=280)
    s = make_sheet(580)
    s.draw(base, font_size=34, fills={(SLIP[0] + 1, 6): RED_T} if t > 0.35 else None)
    for r in range(1, 6):
        if r == SLIP[0] + 1: continue
        cell_sparkline(base, s.cell_box(r, 6), VALS[NAMES[r - 1]], 1.0, col=LINE)
    r = SLIP[0] + 1
    cell_sparkline(base, s.cell_box(r, 6), VALS[NAMES[r - 1]], ease(seg(t, 0.35, 0.95)), col=RED, width=8)
    a = ease(seg(t, 0.35, 0.6))
    s.outline(base, s.cell_box(r, 6), RED, a=a, width=7)
    formula_bar(base, 60, 1230, W - 120, FX2, t=t, t0=1.0, cps=36,
                colors=[("B3:F3", (200, 130, 0)), ('"red"', RED)], size=fit_formula_size(FX2, W - 120, 46, 30))
    return shake(base, t, 0.35, 0.2, 10)

# ---------- Excel: menu, then drag down ----------
T_XL = 0.3 + 2 * 0.3
def sc_excel(t, D):
    base = background()
    label_card(base, t, 0.0, "EXCEL", GREEN, "Insert > Sparklines", y=280)
    menu_path(base, t, 0.3, ["Insert", "Sparklines", "Line"], 560, size=40, gap=0.3)
    s = make_sheet(700)
    s.draw(base, font_size=34)
    t1 = T_XL + 0.2
    cell_sparkline(base, s.cell_box(1, 6), VALS[NAMES[0]], ease(seg(t, t1, t1 + 0.4)), col=(40, 90, 170))
    t2 = t1 + 0.5
    for r in range(2, 6):          # drag the handle down
        a0 = t2 + (r - 2) * 0.12
        cell_sparkline(base, s.cell_box(r, 6), VALS[NAMES[r - 1]], ease(seg(t, a0, a0 + 0.35)), col=(40, 90, 170))
    if t > t1:
        pr = ease_io(seg(t, t2, t2 + 0.5))
        b0, b1 = s.cell_box(1, 6), s.cell_box(5, 6)
        bot = b0[3] + (b1[3] - b0[3]) * pr
        s.outline(base, [b0[0], b0[1], b0[2], bot], GREEN, width=6)
        d = ImageDraw.Draw(base)
        d.rectangle([b0[2] - 9, bot - 9, b0[2] + 9, bot + 9], fill=GREEN, outline=WHITE, width=3)
    return shake(base, t, t1, 0.2, 10)

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.25, [("Sheets: =SPARKLINE formula", True),
                              ("Excel 2016+ & Mac: Insert menu", True)], y0=720, step=150, size=40)
    s = Sheet(0, 1010, [150, 230], [["Rep", "Trend"]] + [[n, ""] for n in NAMES], row_h=78)
    s.x = (W - s.width()) // 2
    a = ease(seg(t, 0.6, 0.9))
    if a > 0:
        s.draw(base, font_size=32, a=a)
        for r in range(1, 6):
            a0 = 0.7 + 0.1 * r
            cell_sparkline(base, s.cell_box(r, 1), VALS[NAMES[r - 1]], ease(seg(t, a0, a0 + 0.5)), a=a, pad=(18, 14))
    return base

QUESTION = "Sparkline or full chart?"
def sc_outro(t, D):
    return loop_back(outro(t, question=QUESTION), sc_hook(0.0, 2.4), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.4),
    ("02_problem", sc_problem, 2.2),
    ("03_sheets", sc_sheets, 2.4),
    ("04_color", sc_color, 2.2),
    ("05_excel", sc_excel, 2.4),
    ("06_both", sc_both, 2.2),
    ("07_outro", sc_outro, 3.2),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| hook font", HF.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, starts[2] + 1.75, starts[3] + 0.35, starts[4] + T_XL + 0.2])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.4).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
