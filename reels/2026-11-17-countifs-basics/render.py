"""Reel: COUNTIFS - count rows that match two conditions (Excel + Google Sheets).

COUNTIF checks ONE rule: =COUNTIF(C2:C8,">60000") counts every rep over $60K, Ops included (5).
COUNTIFS checks every rule on the same row: =COUNTIFS(B2:B8,"Sales",C2:C8,">60000") -> 3.
Syntax (Microsoft Support + Google Docs Editors Help): COUNTIFS(criteria_range1, criteria1, [criteria_range2, criteria2]...)
All ranges must be the same size; a row is counted only when every pair matches.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> countifs-basics.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "countifs-basics"
DATE = "2026-11-17"
REPS = [("Ana", "Sales", 72000), ("Ben", "Ops", 65000), ("Cara", "Sales", 58000), ("Dev", "Sales", 81000),
        ("Eli", "Ops", 49000), ("Finn", "Sales", 66000), ("Gia", "Ops", 90000)]          # rows 2..8
N = len(REPS)
OVER = [i + 1 for i, (_, _, v) in enumerate(REPS) if v > 60000]                       # sheet rows (1-based data)
SALES = [i + 1 for i, (_, d, _) in enumerate(REPS) if d == "Sales"]
BOTH = [r for r in OVER if r in SALES]
N_ONE, N_BOTH = len(OVER), len(BOTH)        # COUNTIF result, COUNTIFS result

F_ONE = '=COUNTIF(C2:C8,">60000")'
F_BOTH = '=COUNTIFS(B2:B8,"Sales",C2:C8,">60000")'
C_B = (40, 110, 220)      # dept range (blue)
C_C = (200, 120, 0)       # sales range (amber)
BLUE_T = (214, 232, 255)
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)
RED_T = (255, 214, 214)
CW = [230, 230, 270]
ROW_H = 80
FS = 42

def grid(y):
    data = [["Name", "Dept", "Sales"]] + [[n, d, f"${v:,}"] for n, d, v in REPS]
    s = Sheet(0, y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def row_fill(rows, col, ncols=3):
    return {(r, c): col for r in rows for c in range(ncols)}

def bar(base, text, y, colors=None, t=None, t0=0.0, w=960, a=1.0, cps=28):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, cps=cps, colors=colors, a=a,
                size=fit_formula_size(text, w, max_size=50))

# ---------- scenes ----------
HOOK = ["WRONG", "COUNT?"]
HOOK2 = ["JUST ADD", "AN S"]
HOOK_FONT = fit_font("Bold", max(HOOK + HOOK2, key=lambda x: F("Bold", 100).getlength(x)), 960, 210)
FLIP = 1.1

def sc_hook(t, D):
    base = background()
    fixed = t >= FLIP
    if not fixed:
        pop_text(base, HOOK[0], W / 2, 365, HOOK_FONT, AMBER, t, -0.3, stroke=10)
        pop_text(base, HOOK[1], W / 2, 555, HOOK_FONT, AMBER, t, -0.2, stroke=10)
    else:
        pop_text(base, HOOK2[0], W / 2, 365, HOOK_FONT, AMBER, t, FLIP - 0.05, stroke=10, dur=0.25)
        pop_text(base, HOOK2[1], W / 2, 555, HOOK_FONT, GREEN, t, FLIP, stroke=10, dur=0.25)
    s = grid(700)
    if fixed: f = row_fill([r for r in BOTH if t >= FLIP + BOTH.index(r) * 0.07], GREEN_T)
    else: f = row_fill(OVER, RED_T)
    s.draw(base, fills=f, font_size=FS)
    if fixed:
        result_chip(base, W / 2, 1490, f"COUNTIFS = {N_BOTH}", True, t, FLIP)
    else:
        result_chip(base, W / 2, 1490, f"COUNTIF = {N_ONE}", False, t, -0.2)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, FLIP, 0.2, 10)

def sc_why(t, D):
    base = background()
    label_card(base, t, 0.0, "WHY?", RED, "COUNTIF checks 1 rule", y=290)
    bar(base, F_ONE, 520, colors=[("C2:C8", C_C)], t=t, t0=0.15, cps=60)
    s = grid(700)
    f = {}
    for k, r in enumerate(OVER):
        if t >= 0.6 + k * 0.1: f.update(row_fill([r], RED_T if r not in SALES else AMBER_T))
    s.draw(base, fills=f, font_size=FS)
    d = ImageDraw.Draw(base)
    for r in OVER:   # Ops reps over 60K got counted too
        if r in SALES: continue
        rad = back(seg(t, 1.3, 1.55)) * 30
        b = s.cell_box(r, 1)
        if rad > 2: cross_icon(d, s.x + s.width() + 4, (b[1] + b[3]) / 2, rad)
    result_chip(base, W / 2, 1490, "Ops got counted", False, t, 1.5)
    return base

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Add an S: COUNTIFS", y=290)
    bar(base, F_BOTH, 520, colors=[("B2:B8", C_B), ('"Sales"', C_B), ("C2:C8", C_C), ('">60000"', C_C)],
        t=t, t0=0.2, cps=48)
    s = grid(700)
    f = {}
    for k, r in enumerate(SALES):   # rule 1 sweeps the Dept column
        if t >= 1.0 + k * 0.08: f[(r, 1)] = BLUE_T
    for k, r in enumerate(OVER):    # rule 2 sweeps the Sales column
        if t >= 1.45 + k * 0.08: f[(r, 2)] = AMBER_T
    for k, r in enumerate(BOTH):    # rows where both match turn green
        if t >= 2.0 + k * 0.08: f.update(row_fill([r], GREEN_T))
    s.draw(base, fills=f, font_size=FS)
    s.outline(base, s.col_box(1), C_B, a=ease(seg(t, 0.9, 1.1)) * (1 - seg(t, 1.9, 2.1)), width=6)
    s.outline(base, s.col_box(2), C_C, a=ease(seg(t, 1.35, 1.55)) * (1 - seg(t, 1.9, 2.1)), width=6)
    result_chip(base, W / 2, 1490, f"Count = {N_BOTH}", True, t, 2.25)
    return shake(base, t, 2.25, 0.2, 10)

def sc_args(t, D):
    base = background()
    label_card(base, t, 0.0, "HOW IT READS", AMBER, "Range, then its rule", y=290)
    arg_rows(base, t, 0.35, [('B2:B8,"Sales"', C_B, "rule 1"), ('C2:C8,">60000"', C_C, "rule 2")],
             y0=760, step=170, size=46, tok_size=44)
    result_chip(base, W / 2, 1180, "Both must match", True, t, 1.3)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.3, [("Excel 365 & 2016+", True), ("Google Sheets", True),
                             ('Put rules in quotes: ">60000"', None)], y0=680, step=160, size=44)
    return base

def sc_outro(t, D):
    return loop_back(outro(t), sc_hook(0.0, 2.6), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.6),
    ("02_why", sc_why, 2.6),
    ("03_fix", sc_fix, 3.2),
    ("04_args", sc_args, 2.6),
    ("05_both", sc_both, 2.4),
    ("06_outro", sc_outro, 2.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| COUNTIF", N_ONE, OVER, "| COUNTIFS", N_BOTH, BOTH, "| hook font", HOOK_FONT.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, FLIP, starts[2] + 2.25])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.6).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
