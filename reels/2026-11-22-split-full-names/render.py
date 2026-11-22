"""Reel: split full names into first and last (cleaning).

Excel: type ONE example next to the data, then Ctrl+E (or Data > Flash Fill) fills the rest of the column
by pattern (Microsoft Support "Using Flash Fill in Excel"; applies to Excel 365, 2024, 2021, 2019, 2016, Mac 2021/2024).
Google Sheets: =SPLIT(A2, " ") puts each piece in its own cell in the row
(Google Docs Editors Help: SPLIT(text, delimiter, [split_by_each], [remove_empty_text])).
All names have exactly one space, so SPLIT returns exactly 2 cells and the results below are computed from the table.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> split-full-names.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "split-full-names"
DATE = "2026-11-22"
NAMES = ["Ana Ruiz", "Ben Carter", "Cara Patel", "Dev Nolan", "Eli Brooks", "Finn Wade"]   # A2:A7
PARTS = [n.split(" ") for n in NAMES]                  # what SPLIT(A2," ") / Flash Fill produce
assert all(len(p) == 2 for p in PARTS)
FIRST = [p[0] for p in PARTS]; LAST = [p[1] for p in PARTS]
N = len(NAMES)
ROWS = list(range(1, N + 1))

F_SPLIT = '=SPLIT(A2, " ")'
C_A = (200, 120, 0)
GREEN_T = (210, 244, 226)
RED_T = (255, 214, 214)
AMBER_T = (255, 236, 196)
CW = [370, 250, 250]
ROW_H = 70
FS = 38

def grid(y, first=None, last=None, hdr=("Full name", "First", "Last")):
    first = first or [""] * N; last = last or [""] * N
    data = [list(hdr)] + [[NAMES[i], first[i], last[i]] for i in range(N)]
    s = Sheet(0, y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def typed(word, t, t0, cps=9):
    k = int(clamp((t - t0) * cps / max(1, len(word))) * len(word))
    return word[:k]

def cursor(base, s, r, c, a=1.0):
    if a > 0: s.outline(base, s.cell_box(r, c), GREEN, a=a, width=6)

def bar(base, text, y, colors=None, t=None, t0=0.0, w=960, cps=28):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, cps=cps, colors=colors,
                size=fit_formula_size(text, w, max_size=56))

# ---------- scenes ----------
HOOK = ["SPLIT", "NAMES?"]
HOOK_FONT = fit_font("Bold", max(HOOK, key=lambda x: F("Bold", 100).getlength(x)), 960, 190)
FLIP = 1.0

def sc_hook(t, D):
    base = background()
    pop_text(base, HOOK[0], W / 2, 340, HOOK_FONT, WHITE if t < FLIP else GREEN, t, -0.3, stroke=10)
    pop_text(base, HOOK[1], W / 2, 530, HOOK_FONT, AMBER, t, -0.2, stroke=10)
    done = t >= FLIP
    s = grid(660, FIRST if done else None, LAST if done else None)
    if done:
        f = sweep_fills([(r, c) for r in ROWS for c in (1, 2)], t, FLIP, GREEN_T, col_gap=0.05, row_gap=0.05)
    else:
        f = {(r, 0): RED_T for r in ROWS if t >= 0.2 + r * 0.06}
    s.draw(base, fills=f, font_size=FS)
    if done: result_chip(base, W / 2, 1450, "Ctrl + E did all 6", True, t, FLIP + 0.1)
    else: result_chip(base, W / 2, 1450, "First + last stuck", False, t, -0.2)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, FLIP, 0.2, 10)

def sc_type(t, D):
    base = background()
    label_card(base, t, 0.0, "STEP 1", AMBER, "Type ONE example", y=290)
    w = typed(FIRST[0], t, 0.45)
    s = grid(600, [w] + [""] * (N - 1))
    s.draw(base, fills={(1, 1): AMBER_T} if t >= 0.4 else {}, font_size=FS)
    cursor(base, s, 1, 1, ease(seg(t, 0.3, 0.45)))
    if t >= 1.3:
        result_chip(base, W / 2, 1420, "Excel learns the pattern", True, t, 1.3)
    return base

def sc_ctrl_e(t, D, col=1, word_list=FIRST, tag="STEP 2", title="Press Ctrl + E", t_press=0.55):
    base = background()
    label_card(base, t, 0.0, tag, AMBER, title, y=290)
    other = FIRST if col == 2 else [""] * N
    vals = [word_list[0]] + [word_list[i] if t >= t_press + 0.15 + i * 0.09 else "" for i in range(1, N)]
    s = grid(600, other if col == 2 else vals, vals if col == 2 else None)
    f = {(r, 1): GREEN_T for r in ROWS} if col == 2 else {}
    f.update({(r, col): GREEN_T for r in ROWS if r == 1 or t >= t_press + 0.15 + (r - 1) * 0.09})
    s.draw(base, fills=f, font_size=FS)
    keycaps(base, t, t_press - 0.25, ["Ctrl", "+", "E"], 1300, size=52, gap=0.25)
    if t >= t_press + 0.9:
        result_chip(base, W / 2, 1500, f"{N} names filled", True, t, t_press + 0.9)
    return shake(base, t, t_press + 0.15, 0.2, 9)

def sc_last(t, D):
    base = background()
    t_type = 0.0
    w = typed(LAST[0], t, 0.3, cps=10)
    if t < 1.1:
        label_card(base, t, 0.0, "STEP 3", AMBER, "Same for last name", y=290)
        s = grid(600, FIRST, [w] + [""] * (N - 1))
        f = {(r, 1): GREEN_T for r in ROWS}; f[(1, 2)] = AMBER_T
        s.draw(base, fills=f, font_size=FS)
        cursor(base, s, 1, 2, ease(seg(t, 0.15, 0.3)))
        return base
    return sc_ctrl_e(t - 1.1 + 0.3, D, col=2, word_list=LAST, tag="STEP 3", title="Same for last name", t_press=0.35)

def sc_sheets(t, D):
    base = background()
    label_card(base, t, 0.0, "GOOGLE SHEETS", BLUE, "One formula, two cells", y=290)
    bar(base, F_SPLIT, 492, colors=[("A2", C_A)], t=t, t0=0.15, cps=30)
    t_res = 0.95
    show = [i for i in range(N) if t >= t_res + i * 0.1]
    s = grid(630, [FIRST[i] if i in show else "" for i in range(N)], [LAST[i] if i in show else "" for i in range(N)])
    f = {(r, 0): AMBER_T for r in (1,)} if t >= 0.6 else {}
    f.update({(i + 1, c): GREEN_T for i in show for c in (1, 2)})
    s.draw(base, fills=f, font_size=FS)
    if t >= t_res + 0.7:
        result_chip(base, W / 2, 1450, "Fill it down: done", True, t, t_res + 0.7)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.3, [("Excel 2016+: Ctrl + E", True), ("Or Data > Flash Fill", True),
                             ('Sheets: =SPLIT(A2," ")', True)], y0=680, step=160, size=44)
    return base

def sc_outro(t, D):
    return loop_back(outro(t), sc_hook(0.0, 2.4), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.4),
    ("02_type", sc_type, 2.2),
    ("03_ctrle", sc_ctrl_e, 2.4),
    ("04_last", sc_last, 2.6),
    ("05_sheets", sc_sheets, 2.8),
    ("06_both", sc_both, 2.3),
    ("07_outro", sc_outro, 2.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| first", FIRST, "| last", LAST, "| hook font", HOOK_FONT.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, FLIP, starts[2] + 0.55])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.4).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
