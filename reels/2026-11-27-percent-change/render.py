"""Reel: Percent change the right way (quiz_open hook).

Excel (Microsoft Support "Calculate percentages"): percentage change = (new - original) / original, e.g. =(2500-2342)/2342,
then Home tab > Percent Style. Google Sheets: same formula; Format as percentage = Ctrl+Shift+5 (Docs Editors Help 181110,
same keys listed for PC and Mac); TO_PERCENT(value) is the function equivalent (help 3094284).
The common mistake is dividing by the NEW value: (100-80)/100 = 20% instead of (100-80)/80 = 25%.
Every value on screen is computed from the tables below.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> percent-change.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from hooks import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "percent-change"
DATE = "2026-11-27"
GREEN_T, RED_T, AMBER_T = (214, 242, 228), (253, 222, 223), (255, 240, 206)

def pct(old, new): return (new - old) / old
def fmt(x): return f"{x:+.0%}".replace("+", "") if x >= 0 else f"{x:.0%}"

# ---------- 1. hook: quiz_open ----------
OLD, NEW = 80, 100
RIGHT = f"{pct(OLD, NEW):.0%}"            # 25%
WRONG = f"{(NEW - OLD) / NEW:.0%}"        # 20% (dividing by the new value)
assert (RIGHT, WRONG) == ("25%", "20%")
Q_DATA = [["Before", "Now", "Change"], [f"${OLD}", f"${NEW}", "?"]]
T_REV = 1.8
D_HOOK = 2.4

def sc_hook(t, D):
    base = screen_bg()
    s = big_sheet([r[:] for r in Q_DATA], [10, 10, 10], y=540, row_h=210)
    rv = t >= T_REV
    if rv: s.data[1][2] = RIGHT
    s.draw(base, font_size=64, fills={(1, 2): GREEN_T if rv else AMBER_T},
           text_cols={(1, 2): GREEN if rv else (200, 130, 0)})
    s.outline(base, s.cell_box(1, 2), GREEN if rv else AMBER, width=8)
    sticker(base, "What's the % change?", 390, t, -0.2, size=78)
    quiz_cards(base, t, WRONG, RIGHT, "b", y=1090, t_in=0.0, t_reveal=T_REV, h=320, size=120)
    fr = camera(base, t, 0.0, T_REV, 1.0, 1.03, focus=(0.5, 0.52))
    return shake_bg(fr, t, T_REV, 0.3, 16)

# ---------- 2. the trap ----------
def sc_trap(t, D):
    base = background()
    label_card(base, t, 0.0, "THE TRAP", RED, "Divide by the OLD value", y=300)
    value_row(base, t, 0.35, 820, f"({NEW}-{OLD})/{NEW} = {WRONG}", ok=False, label="NEW", hot=f"/{NEW}", size=58)
    value_row(base, t, 1.0, 1130, f"({NEW}-{OLD})/{OLD} = {RIGHT}", ok=True, label="OLD", size=58)
    return shake(base, t, 1.0, 0.2, 10)

# ---------- 3. the fix on a real table ----------
ROWS = [("Rent", 1200, 1260), ("Sales", 80, 100), ("Ads", 500, 400), ("Users", 250, 325)]
CH = [pct(o, n) for _, o, n in ROWS]
CHS = [fmt(x) for x in CH]
assert CHS == ["5%", "25%", "-20%", "30%"], CHS
FX = "=(C2-B2)/B2"
CW = [230, 210, 210, 260]

def fix_sheet(y, vals):
    data = [["Item", "Old", "New", "Change"]] + [[n, f"{o:,}", f"{nw:,}", v] for (n, o, nw), v in zip(ROWS, vals)]
    s = Sheet(0, y, CW, data, row_h=112)
    s.x = (W - s.width()) // 2
    return s

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "One formula, every row", y=290)
    vals, fills, cols = [], {}, {}
    for i, v in enumerate(CHS):
        t0 = 0.3 + i * 0.16
        on = t >= t0
        vals.append(v if on else "")
        if on:
            neg = CH[i] < 0
            fills[(i + 1, 3)] = RED_T if neg else GREEN_T
            cols[(i + 1, 3)] = (190, 50, 56) if neg else (16, 120, 74)
    s = fix_sheet(600 + int(24 * (1 - ease(seg(t, 0, 0.4)))), vals)
    s.draw(base, font_size=46, fills=fills, text_cols=cols)
    if t >= 0.3: s.outline(base, s.col_box(3), AMBER, width=7)
    formula_bar(base, 140, 1300, W - 280, FX, t=t, t0=1.3, cps=18,
                colors=[("C2", BLUE), ("B2", (200, 130, 0))], size=64)
    return shake(base, t, 0.3 + 3 * 0.16, 0.2, 10)

# ---------- 4. format as % ----------
RAW = f"{pct(OLD, NEW):g}"                 # 0.25
T_KEY = 0.35 + 2 * 0.22
def sc_format(t, D):
    base = background()
    label_card(base, t, 0.0, f"SHOWS {RAW}?", AMBER, "Format it as %", y=290)
    on = t >= T_KEY
    s = Sheet(0, 560, [420], [["Change"], [RIGHT if on else RAW]], row_h=150)
    s.x = (W - s.width()) // 2
    s.draw(base, font_size=76, fills={(1, 0): GREEN_T if on else AMBER_T},
           text_cols={(1, 0): (16, 120, 74) if on else (200, 130, 0)})
    s.outline(base, s.cell_box(1, 0), GREEN if on else AMBER, width=7)
    d = ImageDraw.Draw(base)
    a1 = ease(seg(t, 0.2, 0.45))
    if a1 > 0: pill(d, W / 2, 1000, "SHEETS", BLUE, size=34, a=a1)
    keycaps(base, t, 0.35, ["Ctrl", "+", "Shift", "+", "5"], 1110, size=46)
    a2 = ease(seg(t, 1.2, 1.45))
    if a2 > 0: pill(d, W / 2, 1290, "EXCEL", GREEN, size=34, a=a2)
    menu_path(base, t, 1.3, ["Home", "% Percent Style"], 1400, size=44, gap=0.3)
    return shake(base, t, T_KEY, 0.2, 10)

# ---------- 5. works in ----------
def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.25, [("Same formula in both", True),
                              ("Negative % = a drop", None)], y0=760, step=160, size=46)
    a = ease(seg(t, 0.8, 1.1))
    if a > 0:
        s = Sheet(0, 1060, [200, 230], [["Item", "Change"]] + [[n, v] for (n, _, _), v in zip(ROWS, CHS)], row_h=72)
        s.x = (W - s.width()) // 2
        s.draw(base, font_size=34, a=a, fills={(i + 1, 1): RED_T if CH[i] < 0 else GREEN_T for i in range(4)},
               text_cols={(i + 1, 1): (190, 50, 56) if CH[i] < 0 else (16, 120, 74) for i in range(4)})
    return base

QUESTION = "Did you pick A or B?"
def sc_outro(t, D):
    return loop_back(outro(t, question=QUESTION), sc_hook(0.0, D_HOOK), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, D_HOOK),
    ("02_trap", sc_trap, 2.4),
    ("03_fix", sc_fix, 2.8),
    ("04_format", sc_format, 2.4),
    ("05_both", sc_both, 2.2),
    ("06_outro", sc_outro, 3.2),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES))
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, T_REV, starts[1] + 1.0, starts[3] + T_KEY])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, D_HOOK).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
