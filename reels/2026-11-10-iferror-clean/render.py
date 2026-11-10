"""Reel: IFERROR - hide ugly #DIV/0! and #N/A errors (Excel + Google Sheets).

=IFERROR(value, value_if_error): returns value, or value_if_error when value is an error
(#N/A, #VALUE!, #REF!, #DIV/0!, #NUM!, #NAME?, #NULL!).
Excel: both arguments required. Google Sheets: value_if_error optional (blank when omitted).
Warning: it hides EVERY error, including typos (#NAME?).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> iferror-clean.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "iferror-clean"
DATE = "2026-11-10"
# (product, sales, units) ; units None = blank cell
ROWS = [("Mugs", 480, 40), ("Caps", 0, 0), ("Totes", 750, 30), ("Socks", 300, None), ("Pens", 135, 45)]
N = len(ROWS); LAST = N + 1

def money(v): return f"${v:,.2f}" if isinstance(v, float) else f"${v:,}"
def price(sales, units):
    """Sales/Units the way a spreadsheet does it: blank or 0 divisor -> #DIV/0!."""
    if not units: return "#DIV/0!"
    return money(sales / units)

RAW = [price(s, u) for _, s, u in ROWS]                         # =B2/C2 filled down
ERR_ROWS = [i + 1 for i, v in enumerate(RAW) if v.startswith("#")]
OK_ROWS = [i + 1 for i, v in enumerate(RAW) if not v.startswith("#")]
CLEAN = ["" if v.startswith("#") else v for v in RAW]          # =IFERROR(B2/C2,"")
MSG = "No units"
MSGD = [MSG if v.startswith("#") else v for v in RAW]          # =IFERROR(B2/C2,"No units")

BASE = [["Product", "Sales", "Units", "Price"]] + [[p, money(s), "" if u is None else str(u), ""] for p, s, u in ROWS]
def data_with(col):
    return [r[:] for r in BASE[:1]] + [BASE[i + 1][:3] + [col[i]] for i in range(N)]

F_RAW = "=B2/C2"
F_FIX = '=IFERROR(B2/C2,"")'
F_MSG = f'=IFERROR(B2/C2,"{MSG}")'
INNER = "B2/C2"

CW = [230, 200, 170, 260]
ROW_H = 82
FS = 38
SHEET_Y = 660
BAR_Y = 1245
CHIP_Y = 1450
RED_T = (253, 222, 222)
GREEN_T = (210, 244, 226)
BLUE_T = (214, 232, 255)
C_IN = (40, 110, 220)
C_ALT = (200, 120, 0)

def sheet(data, y=SHEET_Y):
    s = Sheet(0, y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def bar(base, text, t=None, t0=0.0, colors=None, size=40, w=900, y=BAR_Y, a=1.0):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, colors=colors, size=size, a=a)

# ---------- scenes ----------
def mini(base, x, title, vals, bad, t, t0, y=1000):
    """One-column 'Price' sheet used in the hook before/after."""
    p = ease(seg(t, t0, t0 + 0.3))
    if p <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = Sheet(x, y + (1 - p) * 40, [360], [["Price"]] + [[v] for v in vals], row_h=76, letters=["D"])
    fills, tc = {}, {}
    for r in range(1, len(vals) + 1):
        if vals[r - 1].startswith("#"): fills[(r, 0)] = RED_T; tc[(r, 0)] = RED
        elif not bad: fills[(r, 0)] = GREEN_T
    s.draw(lay, a=p, fills=fills, text_cols=tc, font_size=38)
    d = ImageDraw.Draw(lay)
    pill(d, x + s.width() / 2, y - 70 + (1 - p) * 40, title, RED if bad else GREEN, size=36, a=p)
    base.alpha_composite(lay)
    r = back(seg(t, t0 + 0.3, t0 + 0.55)) * 46
    if r > 2: (cross_icon if bad else check_icon)(ImageDraw.Draw(base), x + s.width() - 10, y - 70, r)

def sc_hook(t, D):
    base = background()
    pop_text(base, "HIDE", W / 2, 420, F("Bold", 200), AMBER, t, -0.15, stroke=10)
    pop_text(base, "ugly #DIV/0! errors", W / 2, 600, F("Bold", 92), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 745, "1 WRAPPER  ·  0 ERRORS", AMBER, fg=NAVY, size=40, a=ease(seg(t, 0.3, 0.55)))
    mini(base, 64, "BEFORE", RAW, True, t, 0.4, y=960)
    mini(base, 64 + 424 + 40, "AFTER", CLEAN, False, t, 0.9, y=960)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "THE PROBLEM", RED, "Price per unit\n= Sales / Units", y=290)
    shown = [RAW[i] if t > 1.6 + i * 0.18 else "" for i in range(N)]
    fills, tc = {}, {}
    if t > 0.8:
        fills.update({(r, 1): BLUE_T for r in range(1, N + 1)}); fills.update({(r, 2): BLUE_T for r in range(1, N + 1)})
    for i, v in enumerate(shown):
        if v.startswith("#"): fills[(i + 1, 3)] = RED_T; tc[(i + 1, 3)] = RED
    s = sheet(data_with(shown))
    s.draw(base, fills=fills, text_cols=tc, font_size=FS)
    if t > 2.9:
        for r in ERR_ROWS:
            s.outline(base, s.cell_box(r, 2), RED, a=ease(seg(t, 2.9, 3.2)))
    bar(base, F_RAW, t, 0.5, size=46)
    result_chip(base, W / 2, CHIP_Y, "Units 0 or blank = #DIV/0!", False, t, 3.1)
    return base

FIX_COLORS = [(INNER, C_IN), ('""', C_ALT)]

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Wrap it in IFERROR", sub='Error? Show "" (a blank) instead.')
    done = t > 2.0
    col = CLEAN if done else RAW
    fills, tc = {}, {}
    for r in ERR_ROWS:
        if not done: fills[(r, 3)] = RED_T; tc[(r, 3)] = RED
        else: fills[(r, 3)] = GREEN_T if int((t - 2.0) * 6) % 2 == 0 or t > 2.6 else RED_T
    if done:
        for r in OK_ROWS: fills[(r, 3)] = GREEN_T
    s = sheet(data_with(col))
    s.draw(base, fills=fills, text_cols=tc, font_size=FS)
    if done: s.outline(base, s.col_box(3), GREEN, a=ease(seg(t, 2.0, 2.3)))
    bar(base, F_FIX, t, 0.4, colors=FIX_COLORS, size=44)
    result_chip(base, W / 2, CHIP_Y, "Clean column", True, t, 2.4)
    return base

def sc_message(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Show a message instead", sub="Any text, 0, or a dash works.")
    done = t > 1.9
    col = MSGD if done else CLEAN
    fills, tc = {}, {}
    if done:
        for r in ERR_ROWS: fills[(r, 3)] = (255, 236, 196); tc[(r, 3)] = (170, 95, 0)
    s = sheet(data_with(col))
    s.draw(base, fills=fills, text_cols=tc, font_size=FS)
    bar(base, F_MSG, t, 0.4, colors=[(INNER, C_IN), (f'"{MSG}"', C_ALT)], size=40)
    result_chip(base, W / 2, CHIP_Y, f'"{MSG}" where it failed', True, t, 2.3)
    return base

def sc_warn(t, D):
    base = background()
    label_card(base, t, 0.0, "WATCH OUT", RED, "It hides EVERY error", y=290)
    bar(base, '=IFERROR(SUMM(B2:B6),"")', size=42, y=560, a=ease(seg(t, 0.3, 0.6)), colors=[("SUMM", RED)])
    info_rows(base, t, 0.9, [("#DIV/0!  #N/A  #VALUE!  #REF!", None),
                             ("Typo SUMM = #NAME?, hidden too", False),
                             ("Fix real mistakes first", True),
                             ("Then wrap the expected ones", True)], y0=800, step=160, size=42)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=380)
    info_rows(base, t, 0.4, [("Excel 365, 2016+, web, Mac", True), ("Google Sheets", True),
                             ("Excel: 2nd argument required", None),
                             ("Sheets: optional, blank if left out", None)], y0=700, step=160, size=40)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_problem", sc_problem, 4.8),
    ("03_fix", sc_fix, 5.8),
    ("04_message", sc_message, 4.6),
    ("05_warn", sc_warn, 4.6),
    ("06_both", sc_both, 4.0),
    ("07_outro", sc_outro, 3.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), RAW, CLEAN, MSGD, ERR_ROWS)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 0.95, starts[2] + 2.0, starts[3] + 1.9])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
