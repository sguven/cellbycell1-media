"""Reel: Why your lookup fails - hidden spaces. TRIM fixes it (every Excel version + Google Sheets).

TRIM(text): removes leading/trailing spaces and collapses repeated inner spaces to one (Excel + Sheets).
Neither TRIM nor Sheets' Data > Data cleanup > Trim whitespace removes non-breaking spaces (CHAR 160, web pages).
XLOOKUP: Excel 365 / 2021 / 2024 + Google Sheets; no match and no if_not_found -> #N/A.
Sheets trims text you type into a cell; stray spaces come from paste/imports/formulas.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> trim-extra-spaces.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "trim-extra-spaces"
DATE = "2026-11-13"
ROWS = [("Ava Diaz", 1200), ("Ben Cole  ", 800), (" Cara Lim", 950),
        ("Dev  Shah", 600), ("Eli Park", 1500), ("Fay Wu", 700)]
N = len(ROWS)
KEY = "Ben Cole"
CLEAN = [excel_trim(n) for n, _ in ROWS]

def money(v): return f"${v:,}"
def xlookup(key, look, ret):
    for k, v in zip(look, ret):
        if k.lower() == key.lower(): return v
    return "#N/A"

RAW_RES = xlookup(KEY, [n for n, _ in ROWS], [b for _, b in ROWS])       # =XLOOKUP("Ben Cole",A2:A7,B2:B7)
CLEAN_RES = xlookup(KEY, CLEAN, [b for _, b in ROWS])                    # =XLOOKUP("Ben Cole",C2:C7,B2:B7)
BEN = [n for n, _ in ROWS].index("Ben Cole  ")                           # row index 1 -> spreadsheet row 3
LEN_A3 = len(ROWS[BEN][0])
assert RAW_RES == "#N/A" and CLEAN_RES == 800 and LEN_A3 == 10 and len(KEY) == 8

F_BAD = '=XLOOKUP("Ben Cole",A2:A7,B2:B7)'
F_LEN = '=LEN(A3)'
F_TRIM = '=TRIM(A2)'
F_GOOD = '=XLOOKUP("Ben Cole",C2:C7,B2:B7)'
C_RET = (40, 110, 220)
C_SRC = (200, 120, 0)

CW = [330, 210, 320]
ROW_H = 76
FS = 38
SHEET_Y = 650
BAR_Y = 500
BAR_W = 980
CHIP_Y = 1360
BLUE_T = (214, 232, 255)
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)
FONT = F("Medium", FS)

def sheet(n_clean=0):
    data = [["Name", "Bonus", "Clean"]]
    for i, (n, b) in enumerate(ROWS):
        data.append(["", money(b), CLEAN[i] if i < n_clean else ""])
    s = Sheet(0, SHEET_Y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def draw_names(base, s, reveal):
    """Column A drawn with hidden-space chips; reveal: list of p per row (0 = looks normal)."""
    for i, (n, _) in enumerate(ROWS):
        b = s.cell_box(i + 1, 0)
        space_text(base, b[0] + 22, (b[1] + b[3]) / 2, n, reveal[i], FONT)

def bar(base, text, t=None, t0=0.0, colors=None, y=BAR_Y, w=BAR_W, a=1.0):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, colors=colors, size=fit_formula_size(text, w), a=a)

def col_fill(f, c, col):
    for r in range(1, N + 1): f[(r, c)] = col

# ---------- scenes ----------
def mini(base, x, title, good, t, t0, y=930):
    p = ease(seg(t, t0, t0 + 0.3))
    if p <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rows = ROWS[:3]
    s = Sheet(x, y + (1 - p) * 40, [340], [["Name"]] + [[""] for _ in rows], row_h=70)
    fills = {(2, 0): GREEN_T if good else AMBER_T}
    s.draw(lay, a=p, fills=fills, font_size=36)
    f = F("Medium", 36)
    for i, (n, _) in enumerate(rows):
        b = s.cell_box(i + 1, 0)
        space_text(lay, b[0] + 22, (b[1] + b[3]) / 2, excel_trim(n) if good else n,
                   0 if good else seg(t, t0 + 0.2, t0 + 0.5), f, a=p)
    d = ImageDraw.Draw(lay)
    pill(d, x + s.width() / 2, y - 64 + (1 - p) * 40, title, GREEN if good else NAVY2, size=34, a=p)
    base.alpha_composite(lay)
    # lookup result under each panel
    q = seg(t, t0 + 0.35, t0 + 0.7)
    if q > 0:
        sc = back(q); cy = y + s.height() + 95; cx = x + s.width() / 2
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        txt = money(CLEAN_RES) if good else RAW_RES
        fb = F("Bold", int(56 * sc))
        w = (fb.getlength(txt) + 150); h = 104 * sc
        col = GREEN if good else RED
        d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h / 2, fill=rgba(col, 1))
        (check_icon if good else cross_icon)(d, cx - w / 2 + h / 2, cy, 30 * sc, col=WHITE)
        d.ellipse([cx - w / 2 + h / 2 - 30 * sc, cy - 30 * sc, cx - w / 2 + h / 2 + 30 * sc, cy + 30 * sc], fill=WHITE)
        (check_icon if good else cross_icon)(d, cx - w / 2 + h / 2, cy, 24 * sc, col=col)
        d.text((cx + 30 * sc, cy), txt, font=fb, fill=WHITE, anchor="mm")
        base.alpha_composite(lay)

def sc_hook(t, D):
    base = background()
    pop_text(base, "#N/A?!", W / 2, 410, F("Bold", 210), AMBER, t, -0.15, stroke=10)
    pop_text(base, "HIDDEN SPACES", W / 2, 600, F("Bold", 100), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 745, "1 FUNCTION FIX", AMBER, fg=NAVY, size=40, a=ease(seg(t, 0.3, 0.55)))
    x0 = (W - 2 * 404 - 110) // 2
    mini(base, x0, "BEFORE", False, t, 0.3)
    if t > 0.75:
        a = ease(seg(t, 0.75, 0.95))
        arrow(ImageDraw.Draw(base), x0 + 404 + 18, 1100, x0 + 404 + 92, 1100, AMBER, width=10, head=24, a=a)
    mini(base, x0 + 404 + 110, "AFTER TRIM", True, t, 0.75)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

BAD_COLORS = [("A2:A7", C_SRC), ("B2:B7", C_RET)]
GOOD_COLORS = [("C2:C7", C_SRC), ("B2:B7", C_RET)]

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "THE PROBLEM", RED, "Lookup says #N/A", y=290)
    s = sheet()
    f = {}
    if t > 1.0: col_fill(f, 0, AMBER_T)
    if t > 1.3: col_fill(f, 1, BLUE_T)
    s.draw(base, fills=f, font_size=FS)
    draw_names(base, s, [0] * N)
    s.outline(base, s.cell_box(BEN + 1, 0), RED, a=ease(seg(t, 2.0, 2.3)))
    bar(base, F_BAD, t, 0.4, colors=BAD_COLORS)
    result_chip(base, W / 2, CHIP_Y, "...but Ben IS right there?!", False, t, 2.3)
    return base

def sc_reveal(t, D):
    base = background()
    label_card(base, t, 0.0, "THE CULPRIT", AMBER, "Invisible spaces", y=290)
    s = sheet()
    s.draw(base, font_size=FS)
    rv = [seg(t, 0.5 + 0.25 * i, 0.85 + 0.25 * i) for i in range(N)]
    draw_names(base, s, rv)
    if t > 1.8: s.outline(base, s.cell_box(BEN + 1, 0), AMBER, a=ease(seg(t, 1.8, 2.0)))
    bar(base, F_LEN, t, 1.7)
    result_chip(base, W / 2, CHIP_Y, f"LEN = {LEN_A3}, not {len(KEY)}", False, t, 2.3)
    pop_text(base, "(usually from copy-paste or imports)", W / 2, 1470, F("Medium", 40), MUTED, t, 3.0, stroke=0)
    return base

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "TRIM in a helper column", y=290)
    n_clean = 0 if t <= 1.0 else min(N, 1 + sum(1 for k in range(N - 1) if t > 1.8 + k * 0.18))
    s = sheet(n_clean)
    f = {}
    for r in range(n_clean): f[(r + 1, 2)] = GREEN_T
    s.draw(base, fills=f, font_size=FS)
    draw_names(base, s, [1] * N)
    s.outline(base, s.cell_box(1, 2), AMBER, a=ease(seg(t, 0.3, 0.6)) * (1 - seg(t, 1.7, 1.9)))
    if t > 1.7 and n_clean < N:
        b = s.cell_box(n_clean, 2); s.outline(base, b, GREEN, a=1)
    bar(base, F_TRIM, t, 0.4, colors=[("TRIM", GREEN)])
    pop_text(base, "...then fill down", W / 2, 1295, F("Medium", 40), MUTED, t, 1.7, stroke=0)
    result_chip(base, W / 2, CHIP_Y + 60, "Extra spaces gone", True, t, 3.2)
    return base

def sc_works(t, D):
    base = background()
    label_card(base, t, 0.0, "NOW IT WORKS", GREEN, "Look up the clean column", y=290)
    s = sheet(N)
    f = {}
    if t > 1.2: col_fill(f, 2, AMBER_T)
    if t > 1.5: col_fill(f, 1, BLUE_T)
    if t > 2.0:
        f[(BEN + 1, 2)] = GREEN_T; f[(BEN + 1, 1)] = GREEN_T
    s.draw(base, fills=f, font_size=FS)
    draw_names(base, s, [0] * N)
    if t > 2.0: s.outline(base, s.cell_box(BEN + 1, 1), GREEN, a=ease(seg(t, 2.0, 2.2)))
    bar(base, F_GOOD, t, 0.3, colors=GOOD_COLORS)
    result_chip(base, W / 2, CHIP_Y, f"Found it: {money(CLEAN_RES)}", True, t, 2.3)
    return base

def sc_inplace(t, D):
    base = background()
    label_card(base, t, 0.0, "NO HELPER COLUMN?", AMBER, "Clean it in place", y=290)
    d = ImageDraw.Draw(base)
    a1 = ease(seg(t, 0.4, 0.7))
    if a1 > 0: pill(d, W / 2, 640, "GOOGLE SHEETS", C_RET, size=36, a=a1)
    menu_path(base, t, 0.6, ["Data", "Data cleanup", "Trim whitespace"], 770, size=38)
    a2 = ease(seg(t, 2.2, 2.5))
    if a2 > 0: pill(ImageDraw.Draw(base), W / 2, 980, "EXCEL", C_RET, size=36, a=a2)
    info_rows(base, t, 2.4, [("Copy the TRIM column", None),
                             ("Paste Values over column A", None)], y0=1130, step=150, size=42)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=330)
    info_rows(base, t, 0.4, [("TRIM: every Excel version", True),
                             ("TRIM: Google Sheets", True),
                             ("XLOOKUP: Excel 2021+ & Sheets", None),
                             ("Web-page spaces (CHAR 160)", False)], y0=660, step=160, size=40)
    pop_text(base, "need SUBSTITUTE: TRIM skips non-breaking spaces", W / 2, 1270, F("Medium", 36), MUTED, t, 1.8, stroke=0)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_problem", sc_problem, 4.8),
    ("03_reveal", sc_reveal, 4.8),
    ("04_fix", sc_fix, 5.0),
    ("05_works", sc_works, 4.6),
    ("06_inplace", sc_inplace, 4.8),
    ("07_both", sc_both, 4.4),
    ("08_outro", sc_outro, 3.4),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), CLEAN, RAW_RES, CLEAN_RES, LEN_A3)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 1.1, starts[1] + 2.3, starts[4] + 2.3])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
