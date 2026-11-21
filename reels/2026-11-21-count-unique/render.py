"""Reel: count unique values with one formula (Excel 365/2021+ and Google Sheets).

10 orders, but how many different customers? COUNTA counts every row (10), repeats included.
=COUNTA(UNIQUE(A2:A11)) -> UNIQUE returns the list without repeats, COUNTA counts it -> 6.
Syntax (Microsoft Support): UNIQUE(array, [by_col], [exactly_once]); Excel 365, 2021, 2024, web.
Google Sheets: UNIQUE(range, ...) works the same; Sheets also has COUNTUNIQUE(value1, [value2, ...]).
Range is exact (A2:A11, no blank cells).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> count-unique.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "count-unique"
DATE = "2026-11-21"
ORDERS = [("Ana", 120), ("Ben", 85), ("Ana", 40), ("Cara", 210), ("Dev", 65),
          ("Ben", 150), ("Eli", 95), ("Ana", 70), ("Finn", 180), ("Cara", 55)]     # rows 2..11
NAMES = [n for n, _ in ORDERS]
N_ALL = len([n for n in NAMES if n != ""])                 # COUNTA(A2:A11)
UNIQ = list(dict.fromkeys(NAMES))                          # UNIQUE(A2:A11), first-seen order
N_UNIQ = len(UNIQ)                                         # COUNTA(UNIQUE(A2:A11))
FIRST = [i + 1 for i, n in enumerate(NAMES) if NAMES.index(n) == i]   # sheet data rows (1-based)
REPEAT = [i + 1 for i, n in enumerate(NAMES) if NAMES.index(n) != i]
assert N_ALL == 10 and N_UNIQ == 6 and len(REPEAT) == 4

F_FIX = "=COUNTA(UNIQUE(A2:A11))"
C_A = (200, 120, 0)
GREEN_T = (210, 244, 226)
RED_T = (255, 214, 214)
AMBER_T = (255, 236, 196)
GREY_T = (228, 232, 240)
CW = [380, 260]
ROW_H = 62
FS = 38

def grid(y):
    data = [["Customer", "Order"]] + [[n, f"${v}"] for n, v in ORDERS]
    s = Sheet(0, y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def row_fill(rows, col, ncols=2):
    return {(r, c): col for r in rows for c in range(ncols)}

def bar(base, text, y, colors=None, t=None, t0=0.0, w=960, a=1.0, cps=28):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, cps=cps, colors=colors, a=a,
                size=fit_formula_size(text, w, max_size=54))

# ---------- scenes ----------
HOOK = ["10", "BUYERS?"]
HOOK2 = ["6", "BUYERS!"]
HOOK_FONT = fit_font("Bold", max(HOOK + HOOK2, key=lambda x: F("Bold", 100).getlength(x)), 960, 200)
FLIP = 1.1

def sc_hook(t, D):
    base = background()
    fixed = t >= FLIP
    if not fixed:
        pop_text(base, HOOK[0], W / 2, 360, HOOK_FONT, RED, t, -0.3, stroke=10)
        pop_text(base, HOOK[1], W / 2, 545, HOOK_FONT, AMBER, t, -0.2, stroke=10)
    else:
        pop_text(base, HOOK2[0], W / 2, 360, HOOK_FONT, GREEN, t, FLIP - 0.05, stroke=10, dur=0.25)
        pop_text(base, HOOK2[1], W / 2, 545, HOOK_FONT, AMBER, t, FLIP, stroke=10, dur=0.25)
    s = grid(672)
    if fixed:
        f = row_fill([r for k, r in enumerate(FIRST) if t >= FLIP + k * 0.06], GREEN_T)
        f.update(row_fill(REPEAT, GREY_T))
        st = {(r, 0): ease(seg(t, FLIP + 0.1, FLIP + 0.4)) for r in REPEAT}
    else:
        f = row_fill([r for k, r in enumerate(REPEAT) if t >= 0.25 + k * 0.08], RED_T); st = None
    s.draw(base, fills=f, font_size=FS, strike=st)
    if fixed: result_chip(base, W / 2, 1480, f"Unique = {N_UNIQ}", True, t, FLIP)
    else: result_chip(base, W / 2, 1480, f"COUNTA = {N_ALL}", False, t, -0.2)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, FLIP, 0.2, 10)

def sc_trap(t, D):
    base = background()
    label_card(base, t, 0.0, "THE TRAP", RED, "COUNTA counts repeats", y=290)
    s = grid(560)
    f = {}
    for k, r in enumerate(REPEAT):
        if t >= 0.5 + k * 0.22: f.update(row_fill([r], RED_T))
    s.draw(base, fills=f, font_size=FS)
    for k, r in enumerate(REPEAT):
        b = s.cell_box(r, 0)
        a = ease(seg(t, 0.5 + k * 0.22, 0.7 + k * 0.22))
        if a > 0: s.outline(base, [b[0], b[1], b[2] + CW[1], b[3]], RED, a=a, width=6)
    result_chip(base, W / 2, 1420, f"{len(REPEAT)} repeats counted", False, t, 1.5)
    return shake(base, t, 1.5, 0.2, 8)

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Wrap it in UNIQUE", y=290)
    bar(base, F_FIX, 492, colors=[("A2:A11", C_A)], t=t, t0=0.15, cps=40)
    s = grid(622)
    f = {(r, 0): AMBER_T for r in range(1, 11)} if t >= 0.75 else {}
    st = {}
    if t >= 1.25:
        f = {}
        for k, r in enumerate(REPEAT):
            if t >= 1.25 + k * 0.1: f.update(row_fill([r], GREY_T)); st[(r, 0)] = ease(seg(t, 1.25 + k * 0.1, 1.5 + k * 0.1))
        for k, r in enumerate(FIRST):
            if t >= 1.75 + k * 0.08: f.update(row_fill([r], GREEN_T))
    s.draw(base, fills=f, font_size=FS, strike=st)
    s.outline(base, s.col_box(0), C_A, a=ease(seg(t, 0.7, 0.9)) * (1 - seg(t, 1.2, 1.4)), width=6)
    result_chip(base, W / 2, 1470, f"= {N_UNIQ} customers", True, t, 2.3)
    return shake(base, t, 2.3, 0.2, 10)

def sc_how(t, D):
    base = background()
    label_card(base, t, 0.0, "HOW IT WORKS", AMBER, "UNIQUE drops repeats", y=290)
    left = Sheet(70, 560, [300], [["Customer"]] + [[n] for n in NAMES], row_h=ROW_H)
    right_data = [["UNIQUE"]] + [[n if t >= 0.6 + i * 0.14 else ""] for i, n in enumerate(UNIQ)]
    right = Sheet(W - 70 - 364, 560, [300], right_data, row_h=ROW_H, letters=["D"])
    lf = {(r, 0): GREY_T for r in REPEAT} if t >= 0.4 else {}
    left.draw(base, fills=lf, font_size=FS, text_cols={(r, 0): MUTED for r in REPEAT} if t >= 0.4 else None)
    rf = {(i + 1, 0): GREEN_T for i in range(N_UNIQ) if t >= 0.6 + i * 0.14}
    right.draw(base, fills=rf, font_size=FS)
    d = ImageDraw.Draw(base)
    pa = ease(seg(t, 0.3, 0.6))
    if pa > 0:
        ax0 = left.x + left.width() + 22; ax1 = right.x - 22
        arrow(d, ax0, 900, ax0 + (ax1 - ax0) * pa, 900, AMBER, width=12, head=30, a=pa)
    result_chip(base, W / 2, 1420, f"COUNTA counts {N_UNIQ}", True, t, 1.6)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.3, [("Excel 365 & 2021+", True), ("Google Sheets", True),
                             ("Sheets also: COUNTUNIQUE", None)], y0=680, step=160, size=44)
    return base

def sc_outro(t, D):
    return loop_back(outro(t), sc_hook(0.0, 2.4), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.4),
    ("02_trap", sc_trap, 2.4),
    ("03_fix", sc_fix, 3.0),
    ("04_how", sc_how, 2.6),
    ("05_both", sc_both, 2.3),
    ("06_outro", sc_outro, 2.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| COUNTA", N_ALL, "| UNIQUE", UNIQ, N_UNIQ, "| hook font", HOOK_FONT.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, FLIP, starts[2] + 2.3])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.4).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
