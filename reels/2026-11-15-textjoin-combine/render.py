"""Reel: TEXTJOIN - combine a list into one cell with commas (Excel 2019 / 2021 / 2024 / 365 + Google Sheets).

=TEXTJOIN(delimiter, ignore_empty, text1, [text2], ...)
ignore_empty TRUE skips blank cells; FALSE keeps them (extra delimiters). Over 32,767 chars -> #VALUE! (Excel).
Bonus: =TEXTJOIN(", ",TRUE,FILTER(A2:A7,B2:B7="Sales"))  (FILTER: Excel 365/2021+ and Sheets, not Excel 2019).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> textjoin-combine.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "textjoin-combine"
DATE = "2026-11-15"
ROWS = [("Ava", "Sales"), ("Ben", "Ops"), ("Cara", "Sales"), ("Dev", "HR"), ("Eli", "Sales"), ("Fay", "Ops")]
N = len(ROWS)                                   # data rows 2..7

def textjoin(delim, ignore_empty, items):
    """Same rule as Excel / Sheets TEXTJOIN for a list of cell strings."""
    return delim.join(s for s in items if not (ignore_empty and s == ""))

NAMES = [a for a, _ in ROWS]
RES = textjoin(", ", True, NAMES)                                   # =TEXTJOIN(", ",TRUE,A2:A7)
HOOK_IN = NAMES[:4]
HOOK_RES = textjoin(", ", True, HOOK_IN)                            # A2:A5
BLANKS = ["Ava", "Ben", "", "Dev", "Eli", "Fay"]                    # A4 empty
RES_T = textjoin(", ", True, BLANKS)
RES_F = textjoin(", ", False, BLANKS)
RES_SALES = textjoin(", ", True, [a for a, b in ROWS if b == "Sales"])
OLD = '=A2&", "&A3&", "&A4&", "&A5&", "&A6&", "&A7'

F_MAIN = '=TEXTJOIN(", ",TRUE,A2:A7)'
F_SALES = '=TEXTJOIN(", ",TRUE,FILTER(A2:A7,B2:B7="Sales"))'
C_DEL = (200, 120, 0)       # delimiter (amber)
C_RNG = (40, 110, 220)      # range (blue)
C_BOOL = (20, 140, 90)      # TRUE (green)
MAIN_COLORS = [('", "', C_DEL), ("TRUE", C_BOOL), ("A2:A7", C_RNG)]

CW = [200, 180, 560]
ROW_H = 66
FS = 36
SHEET_Y = 640
BAR_Y = 490
BAR_W = 960
CHIP_Y = 1470
BLUE_T = (214, 232, 255)
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)
RED_T = (255, 214, 214)

def grid(c2="", names=NAMES, rows=8):
    data = [["Name", "Team", "All names"]]
    for i, (a, b) in enumerate(zip(names, [t for _, t in ROWS])):
        data.append([a, b, c2 if i == 0 else ""])
    while len(data) < rows: data.append(["", "", ""])
    s = Sheet(0, SHEET_Y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def bar(base, text, t=None, t0=0.0, colors=None, y=BAR_Y, w=BAR_W, a=1.0):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, colors=colors, size=fit_formula_size(text, w), a=a)

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "TEXTJOIN", W / 2, 420, F("Bold", 190), AMBER, t, -0.15, stroke=10)
    pop_text(base, "a list in ONE cell", W / 2, 600, F("Bold", 104), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 745, "1 FORMULA  ·  NO COPY-PASTE", AMBER, fg=NAVY, size=40, a=ease(seg(t, 0.3, 0.55)))
    # before: names down a column
    p = ease(seg(t, 0.35, 0.65))
    if p > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        s = Sheet(70, 960 + (1 - p) * 40, [200], [["Name"]] + [[n] for n in HOOK_IN], row_h=70)
        s.draw(lay, a=p, fills={(r, 0): AMBER_T for r in range(1, 5)}, font_size=38)
        pill(ImageDraw.Draw(lay), 70 + s.width() / 2, 890 + (1 - p) * 40, "BEFORE", NAVY2, size=36, a=p)
        base.alpha_composite(lay)
    if t > 0.7:
        arrow(ImageDraw.Draw(base), 348, 1200, 412, 1200, AMBER, width=12, head=28, a=ease(seg(t, 0.7, 0.9)))
    q = ease(seg(t, 0.8, 1.1))
    if q > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        s = Sheet(420, 1060 + (1 - q) * 40, [530], [["All names"], [HOOK_RES]], row_h=86, letters=["B"])
        s.draw(lay, a=q, fills={(1, 0): GREEN_T}, font_size=40)
        pill(ImageDraw.Draw(lay), 420 + s.width() / 2, 990 + (1 - q) * 40, "AFTER", GREEN, size=36, a=q)
        base.alpha_composite(lay)
        r = back(seg(t, 1.1, 1.35)) * 46
        if r > 2: check_icon(ImageDraw.Draw(base), 420 + s.width() - 40, 990, r)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_old(t, D):
    base = background()
    label_card(base, t, 0.0, "THE OLD WAY", RED, "Glue every cell by hand", y=330)
    bar(base, OLD, t, 0.4, y=620, w=1000)
    if t > 2.0:
        d = ImageDraw.Draw(base); a = ease(seg(t, 2.0, 2.2))
        cross_icon(d, W - 50, 618, 40 * back(seg(t, 2.0, 2.25)), a=a)
    info_rows(base, t, 2.1, [("One & for every single cell", False),
                             ("New name? Rewrite the formula", False)], y0=880, step=160, size=40)
    pop_text(base, "One function does it all", W / 2, 1290, F("Bold", 64), AMBER, t, 3.1, stroke=6)
    return base

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Type it once in C2", y=280)
    done = t > 1.9
    s = grid(RES if done else "")
    f = {}
    if t > 1.05:
        for r in range(1, N + 1): f[(r, 0)] = BLUE_T
    if done: f[(1, 2)] = GREEN_T
    s.draw(base, fills=f, font_size=FS)
    s.outline(base, s.cell_box(1, 2), AMBER, a=ease(seg(t, 0.3, 0.6)))
    if t > 1.05: s.outline(base, s.col_box(0, 1, N), C_RNG, a=ease(seg(t, 1.05, 1.3)), width=5, dash=True)
    bar(base, F_MAIN, t, 0.35, colors=MAIN_COLORS)
    result_chip(base, W / 2, CHIP_Y, "6 names, 1 cell", True, t, 2.3)
    return base

def sc_how(t, D):
    base = background()
    label_card(base, t, 0.0, "HOW IT WORKS", AMBER, "3 parts, that's it", y=300)
    bar(base, F_MAIN, colors=MAIN_COLORS, y=560, a=ease(seg(t, 0.2, 0.5)))
    arg_rows(base, t, 0.8, [('", "', C_DEL, "what goes between"),
                            ("TRUE", C_BOOL, "skip empty cells"),
                            ("A2:A7", C_RNG, "the cells to join")], y0=850, step=150, size=42)
    pop_text(base, "Swap \", \" for \" / \" or \" - \"", W / 2, 1360, F("Medium", 44), MUTED, t, 2.6, stroke=0)
    return base

def sc_blanks(t, D):
    base = background()
    label_card(base, t, 0.0, "GOT BLANKS?", RED, "TRUE vs FALSE", y=280)
    a = ease(seg(t, 0.3, 0.6))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = Sheet(0, 560, [130] * 6, [BLANKS], row_h=76, letters=list("ABCDEF"), row_labels=["2"])
    s.x = (W - s.width()) // 2
    s.draw(lay, a=a, fills={(0, 2): RED_T} if t > 0.9 else {}, font_size=34)
    base.alpha_composite(lay)
    if t > 0.9: s.outline(base, s.cell_box(0, 2), RED, a=ease(seg(t, 0.9, 1.1)), width=6)
    value_row(base, t, 1.4, 960, RES_T, ok=True, label="TRUE  =  skip the blank", size=40)
    value_row(base, t, 2.6, 1240, RES_F, ok=False, label="FALSE  =  keep it", hot=", ,", size=40)
    return base

def sc_sales(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Only the Sales team", y=280)
    done = t > 2.7
    s = grid(RES_SALES if done else "")
    f = {}
    if t > 1.6:
        for r in range(1, N + 1):
            f[(r, 1)] = AMBER_T
            if ROWS[r - 1][1] == "Sales": f[(r, 0)] = BLUE_T
    if done: f[(1, 2)] = GREEN_T
    s.draw(base, fills=f, font_size=FS)
    s.outline(base, s.cell_box(1, 2), AMBER, a=1.0)
    bar(base, F_SALES, t, 0.3, colors=[('", "', C_DEL), ("TRUE", C_BOOL), ("FILTER", RED), ("A2:A7", C_RNG), ("B2:B7", C_DEL)])
    result_chip(base, W / 2, CHIP_Y, "TEXTJOIN + FILTER", True, t, 3.0)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=330)
    info_rows(base, t, 0.4, [("Excel 365 / 2024 / 2021 / 2019", True), ("Google Sheets", True),
                             ("Excel 2016 or older", False),
                             ("FILTER bonus: 365 / 2021+", None)], y0=660, step=160, size=40)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_old", sc_old, 4.4),
    ("03_fix", sc_fix, 4.8),
    ("04_how", sc_how, 5.0),
    ("05_blanks", sc_blanks, 5.0),
    ("06_sales", sc_sales, 5.2),
    ("07_both", sc_both, 3.8),
    ("08_outro", sc_outro, 3.4),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "|", RES, "|", HOOK_RES, "|", RES_T, "|", RES_F, "|", RES_SALES)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 1.1, starts[2] + 1.9, starts[5] + 2.7])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
