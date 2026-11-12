"""Reel: FILTER - a live filtered table with one formula (Excel 365/2021/2024 + Google Sheets).

Excel:  =FILTER(array, include, [if_empty])        no match + no if_empty -> #CALC!
Sheets: =FILTER(range, condition1, [condition2...]) no match -> #N/A (extra args are MORE conditions, no if_empty)
AND of two tests: (test1)*(test2) works in both. Result spills; keep the cells below empty.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> filter-function.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "filter-function"
DATE = "2026-11-12"
ROWS = [("Ava", "Sales", 1200), ("Ben", "Ops", 800), ("Cara", "Sales", 950),
        ("Dev", "HR", 600), ("Eli", "Sales", 1500), ("Fay", "Ops", 700)]
ROWS_LIVE = [r if r[0] != "Ben" else ("Ben", "Sales", 800) for r in ROWS]   # B3 changed Ops -> Sales
N = len(ROWS)                    # data rows 2..7
OUT_R = 8                        # sheet row index 8 = spreadsheet row 9 (formula lives in A9)
NROWS = 12                       # draw rows 1..12

def money(v): return f"${v:,}"
def flt(rows, test): return [r for r in rows if test(r)]          # what FILTER returns (order kept)

RES = flt(ROWS, lambda r: r[1] == "Sales")                         # =FILTER(A2:C7,B2:B7="Sales")
RES_LIVE = flt(ROWS_LIVE, lambda r: r[1] == "Sales")
RES_AND = flt(ROWS, lambda r: r[1] == "Sales" and r[2] > 1000)     # (B="Sales")*(C>1000)
RES_IT = flt(ROWS, lambda r: r[1] == "IT")                         # empty -> fallback

F_MAIN = '=FILTER(A2:C7,B2:B7="Sales")'
F_AND = '=FILTER(A2:C7,(B2:B7="Sales")*(C2:C7>1000))'
F_XL = '=FILTER(A2:C7,B2:B7="IT","None")'
F_GS = '=IFNA(FILTER(A2:C7,B2:B7="IT"),"None")'
C_RET = (40, 110, 220)      # return range (blue)
C_SRC = (200, 120, 0)       # search / condition range (amber)

CW = [250, 240, 250]
ROW_H = 60
FS = 36
SHEET_Y = 620
BAR_Y = 482
BAR_W = 960
CHIP_Y = 1488
BLUE_T = (214, 232, 255)
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)

def grid(src, out, n_out=None):
    """12-row sheet: header, data rows 2..7, blank row 8, FILTER output from row 9."""
    data = [["Name", "Team", "Bonus"]] + [[a, b, money(c)] for a, b, c in src] + [["", "", ""]]
    shown = out if n_out is None else out[:n_out]
    for a, b, c in shown: data.append([a, b, money(c)])
    while len(data) < NROWS: data.append(["", "", ""])
    s = Sheet(0, SHEET_Y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def bar(base, text, t=None, t0=0.0, colors=None, y=BAR_Y, w=BAR_W, a=1.0, size=None):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, colors=colors,
                size=size or fit_formula_size(text, w), a=a)

def tints(cond_cols=(1,), src_on=True, out_rows=0, out_col=GREEN_T):
    f = {}
    if src_on:
        for r in range(1, N + 1):
            for c in range(3): f[(r, c)] = BLUE_T
            for c in cond_cols: f[(r, c)] = AMBER_T
    for k in range(out_rows):
        for c in range(3): f[(OUT_R + k, c)] = out_col
    return f

# ---------- scenes ----------
def mini(base, x, title, rows, good, hot, t, t0, y=960):
    """Two-column Name/Team mini sheet for the hook before/after."""
    p = ease(seg(t, t0, t0 + 0.3))
    if p <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = Sheet(x, y + (1 - p) * 40, [200, 180], [["Name", "Team"]] + [[a, b] for a, b, _ in rows], row_h=66)
    fills = {}
    for i, r in enumerate(rows):
        if r[1] == "Sales":
            fills[(i + 1, 0)] = fills[(i + 1, 1)] = GREEN_T if good else AMBER_T
    s.draw(lay, a=p, fills=fills, font_size=36)
    d = ImageDraw.Draw(lay)
    pill(d, x + s.width() / 2, y - 70 + (1 - p) * 40, title, GREEN if good else NAVY2, size=36, a=p)
    base.alpha_composite(lay)
    if good:
        r = back(seg(t, t0 + 0.3, t0 + 0.55)) * 46
        if r > 2: check_icon(ImageDraw.Draw(base), x + s.width() - 10, y - 70, r)

def sc_hook(t, D):
    base = background()
    pop_text(base, "FILTER", W / 2, 420, F("Bold", 200), AMBER, t, -0.15, stroke=10)
    pop_text(base, "with ONE formula", W / 2, 600, F("Bold", 96), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 745, "LIVE  ·  NO CLICKS", AMBER, fg=NAVY, size=40, a=ease(seg(t, 0.3, 0.55)))
    mini(base, 76, "ALL DATA", ROWS, False, True, t, 0.35)
    if t > 0.75:
        a = ease(seg(t, 0.75, 0.95))
        arrow(ImageDraw.Draw(base), 76 + 444 + 4, 1180, 76 + 444 + 36, 1180, AMBER, width=10, head=24, a=a)
    mini(base, 76 + 444 + 40, "ONLY SALES", RES, True, False, t, 0.8)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_old(t, D):
    base = background()
    label_card(base, t, 0.0, "THE OLD WAY", RED, "Copy, paste, repeat", y=380)
    info_rows(base, t, 0.5, [("Turn on Filter, untick boxes", False),
                             ("Copy & paste the visible rows", False),
                             ("Data changes? Do it all again", False)], y0=720, step=160, size=40)
    pop_text(base, "There's a 1-formula way", W / 2, 1290, F("Bold", 64), AMBER, t, 2.4, stroke=6)
    return base

MAIN_COLORS = [("A2:C7", C_RET), ("B2:B7", C_SRC)]

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Type it once in A9", y=290)
    n_out = sum(1 for k in range(len(RES)) if t > 1.9 + k * 0.2)
    s = grid(ROWS, RES, n_out)
    f = {}
    if t > 0.85:
        for r in range(1, N + 1):
            for c in range(3): f[(r, c)] = BLUE_T
    if t > 1.15:
        for r in range(1, N + 1): f[(r, 1)] = AMBER_T
    f.update(tints(src_on=False, out_rows=n_out))
    s.draw(base, fills=f, font_size=FS)
    s.outline(base, s.cell_box(OUT_R, 0), AMBER, a=ease(seg(t, 0.3, 0.6)))
    if n_out == len(RES):
        b0, b1 = s.cell_box(OUT_R, 0), s.cell_box(OUT_R + n_out - 1, 2)
        s.outline(base, [b0[0], b0[1], b1[2], b1[3]], (40, 110, 220), a=ease(seg(t, 2.5, 2.8)), width=5, dash=True)
    bar(base, F_MAIN, t, 0.4, colors=MAIN_COLORS)
    result_chip(base, W / 2, CHIP_Y, f"{len(RES)} Sales rows, spilled", True, t, 2.7)
    return base

def sc_live(t, D):
    base = background()
    label_card(base, t, 0.0, "IT'S LIVE", AMBER, "Change the data...", y=290)
    changed = t > 1.3
    src = ROWS_LIVE if changed else ROWS
    out = RES_LIVE if t > 1.8 else RES
    s = grid(src, out)
    f = tints(src_on=False, out_rows=len(out))
    if changed:
        f[(2, 1)] = AMBER if int((t - 1.3) * 6) % 2 == 0 and t < 2.0 else AMBER_T
    if t > 1.8:
        k = OUT_R + [r[0] for r in out].index("Ben")
        for c in range(3): f[(k, c)] = AMBER_T if int((t - 1.8) * 6) % 2 == 0 and t < 2.6 else GREEN_T
    s.draw(base, fills=f, font_size=FS)
    if changed: s.outline(base, s.cell_box(2, 1), AMBER, a=ease(seg(t, 1.3, 1.5)))
    bar(base, F_MAIN, colors=MAIN_COLORS)
    result_chip(base, W / 2, CHIP_Y, "...it updates by itself", True, t, 2.4)
    return base

def sc_and(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "2 conditions? Multiply", y=290)
    n_out = len(RES_AND) if t > 2.6 else 0
    s = grid(ROWS, RES_AND, n_out)
    f = tints(cond_cols=(1, 2), src_on=t > 1.2, out_rows=n_out)
    s.draw(base, fills=f, font_size=FS)
    s.outline(base, s.cell_box(OUT_R, 0), AMBER, a=1.0)
    bar(base, F_AND, t, 0.4, colors=[("A2:C7", C_RET), ("B2:B7", C_SRC), ("C2:C7", C_SRC), ("*", RED)])
    result_chip(base, W / 2, CHIP_Y, "Sales AND over $1,000", True, t, 2.9)
    return base

def sc_empty(t, D):
    base = background()
    label_card(base, t, 0.0, "NO MATCHES?", RED, "Add a fallback", y=290)
    d = ImageDraw.Draw(base)
    a1 = ease(seg(t, 0.4, 0.7)); a2 = ease(seg(t, 1.6, 1.9))
    if a1 > 0:
        pill(d, W / 2, 600, "EXCEL  ·  3rd argument", (40, 110, 220), size=34, a=a1)
        bar(base, F_XL, y=660, a=a1, colors=[('"None"', GREEN)])
    if a2 > 0:
        pill(d, W / 2, 850, "GOOGLE SHEETS  ·  wrap in IFNA", (40, 110, 220), size=34, a=a2)
        bar(base, F_GS, y=910, a=a2, colors=[("IFNA", GREEN), ('"None"', GREEN)])
    info_rows(base, t, 2.6, [("No fallback: Excel #CALC!", None),
                             ("No fallback: Sheets #N/A", None)], y0=1150, step=150, size=40)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=330)
    info_rows(base, t, 0.4, [("Excel 365 / 2021 / 2024", True), ("Google Sheets", True),
                             ("Excel 2019 or older", False),
                             ("Keep the cells below empty", None)], y0=660, step=160, size=40)
    pop_text(base, "(or you get a #SPILL! / #REF! error)", W / 2, 1380, F("Medium", 40), MUTED, t, 1.8, stroke=0)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_old", sc_old, 4.0),
    ("03_fix", sc_fix, 5.2),
    ("04_live", sc_live, 4.8),
    ("05_and", sc_and, 5.0),
    ("06_empty", sc_empty, 5.0),
    ("07_both", sc_both, 4.2),
    ("08_outro", sc_outro, 3.4),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), RES, RES_LIVE, RES_AND, RES_IT)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 1.1, starts[2] + 1.9, starts[3] + 1.8])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
