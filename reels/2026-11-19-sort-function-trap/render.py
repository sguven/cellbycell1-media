"""Reel: SORT - the one difference between Excel and Google Sheets (descending order).

Excel (Microsoft Support): SORT(array, [sort_index], [sort_order], [by_col]); sort_order 1 = ascending (default),
-1 = descending; Excel for Microsoft 365, 2024, 2021 (+ Mac, web, mobile).
Google Sheets (Docs Editors Help): SORT(range, sort_column, is_ascending, [sort_column2, is_ascending2, ...]);
is_ascending TRUE = ascending, FALSE = descending; sort_column and is_ascending are required.
So "biggest first": Excel =SORT(A2:B6,2,-1)  |  Sheets =SORT(A2:B6,2,FALSE). Results computed below.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> sort-function-trap.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "sort-function-trap"
DATE = "2026-11-19"
REPS = [("Ana", 4200), ("Ben", 7950), ("Cara", 3100), ("Dev", 9400), ("Eli", 6050)]     # A2:B6
N = len(REPS)
ORDER = sorted(range(N), key=lambda i: -REPS[i][1])          # SORT(A2:B6, 2, descending)
SORTED = [REPS[i] for i in ORDER]
assert [v for _, v in SORTED] == sorted([v for _, v in REPS], reverse=True)

F_XL = "=SORT(A2:B6,2,-1)"
F_GS = "=SORT(A2:B6,2,FALSE)"
C_RANGE = (200, 120, 0)
C_COL = (40, 110, 220)
C_ORD = (200, 40, 60)
GREEN_T = (210, 244, 226)
AMBER_T = (255, 236, 196)

def rows_of(lst): return [[n, f"${v:,}"] for n, v in lst]
HDR = ["Name", "Sales"]

# ---------- hook ----------
HOOK = ["BIGGEST", "ON TOP"]
HOOK_FONT = fit_font("Bold", "BIGGEST", 900, 200)
SORT_T0, SORT_T1 = 0.35, 1.25

def sc_hook(t, D):
    base = background()
    pop_text(base, HOOK[0], W / 2, 370, HOOK_FONT, AMBER, t, -0.3, stroke=10)
    pop_text(base, HOOK[1], W / 2, 570, HOOK_FONT, AMBER, t, -0.2, stroke=10)
    s = Sheet(0, 720, [300, 300], [HDR] + rows_of(REPS), row_h=96)
    s.x = (W - s.width()) // 2
    p = seg(t, SORT_T0, SORT_T1)
    fills = {(0, 0): GREEN_T, (0, 1): GREEN_T}
    moving_rows(base, s, rows_of(REPS), ORDER, p, fills=fills, font_size=46)
    result_chip(base, W / 2, 1450, "Excel -1  ·  Sheets FALSE", True, t, 1.35)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, SORT_T1, 0.2, 10)

# ---------- app scenes ----------
CW = [170, 190]
def pair(y):
    src = Sheet(0, y, CW, [HDR] + rows_of(REPS), row_h=80)
    out = Sheet(0, y, CW, [HDR] + rows_of(SORTED), row_h=80, letters=["D", "E"])
    gap = 56
    src.x = (W - src.width() - out.width() - gap) // 2
    out.x = src.x + src.width() + gap
    return src, out

def app_scene(t, tag, tag_col, title, formula, order_tok, chip):
    base = background()
    label_card(base, t, 0.0, tag, tag_col, title, y=290)
    w = 960
    formula_bar(base, (W - w) // 2, 520, w, formula, t=t, t0=0.2, cps=40,
                colors=[("A2:B6", C_RANGE), (",2,", C_COL), (order_tok, C_ORD)],
                size=fit_formula_size(formula, w, max_size=54))
    src, out = pair(700)
    src.draw(base, font_size=38, a=0.85)
    src.outline(base, src.col_box(0, 1, N)[:2] + src.col_box(1, 1, N)[2:], C_RANGE, a=ease(seg(t, 0.6, 0.8)), width=6)
    t_done = 0.2 + len(formula) / 40
    hdr_only = Sheet(out.x, out.y, CW, [HDR] + [["", ""] for _ in range(N)], row_h=80, letters=["D", "E"])
    k = int(clamp((t - t_done) / 0.09, 0, N))
    if k == 0:
        hdr_only.draw(base, font_size=38)
    else:
        part = Sheet(out.x, out.y, CW, [HDR] + rows_of(SORTED[:k]) + [["", ""]] * (N - k), row_h=80, letters=["D", "E"])
        part.draw(base, font_size=38, fills={(1, 0): GREEN_T, (1, 1): GREEN_T})
    out.outline(base, out.cell_box(1, 0), C_RANGE, a=ease(seg(t, t_done - 0.1, t_done + 0.1)), width=6)
    d = ImageDraw.Draw(base)
    arrow(d, src.x + src.width() + 6, 990, out.x - 6, 990, AMBER, width=8, head=22, a=ease(seg(t, t_done - 0.1, t_done + 0.1)))
    result_chip(base, W / 2, 1450, chip, True, t, t_done + 0.55)
    return shake(base, t, t_done + 0.55, 0.2, 10)

def sc_excel(t, D):
    return app_scene(t, "EXCEL", GREEN, "Biggest first = -1", F_XL, "-1", "Excel: -1")

def sc_sheets(t, D):
    return app_scene(t, "GOOGLE SHEETS", BLUE, "Biggest first = FALSE", F_GS, "FALSE", "Sheets: FALSE")

def sc_trap(t, D):
    base = background()
    label_card(base, t, 0.0, "THE TRAP", RED, "Watch this argument", y=290)
    arg_rows(base, t, 0.35, [("-1", C_ORD, "Excel: high to low"), ("FALSE", C_ORD, "Sheets: high to low"),
                             ("1 / TRUE", C_COL, "Low to high")], y0=720, step=170, size=44, tok_size=44)
    result_chip(base, W / 2, 1330, "Check it when you copy", True, t, 1.5)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.3, [("Excel 365 / 2021 / 2024", True), ("Google Sheets", True),
                             ("Sheets: column + order required", None)], y0=680, step=160, size=42)
    return base

def sc_outro(t, D):
    return loop_back(outro(t), sc_hook(0.0, 2.7), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.7),
    ("02_excel", sc_excel, 2.8),
    ("03_sheets", sc_sheets, 2.9),
    ("04_trap", sc_trap, 2.7),
    ("05_both", sc_both, 2.4),
    ("06_outro", sc_outro, 2.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.3, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| sorted", SORTED, "| hook font", HOOK_FONT.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, SORT_T1, starts[1] + 0.2 + len(F_XL) / 40 + 0.55])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.2, 2.7).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
