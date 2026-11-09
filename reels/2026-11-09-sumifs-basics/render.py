"""Reel: SUMIFS - total sales by person and month (Excel + Google Sheets).

=SUMIFS(sum_range, criteria_range1, criterion1, [criteria_range2, criterion2, ...])
Same syntax in Excel and Google Sheets. Trap: SUMIF puts sum_range LAST, SUMIFS puts it FIRST.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> sumifs-basics.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "sumifs-basics"
ROWS = [("Maya", "Jan", 1200), ("Liam", "Jan", 950), ("Maya", "Feb", 800),
        ("Maya", "Jan", 650), ("Liam", "Feb", 1100), ("Maya", "Feb", 400)]
def money(v): return f"${v:,}"
DATA = [["Rep", "Month", "Sales"]] + [[r, m, money(v)] for r, m, v in ROWS]
N = len(ROWS)                                   # data rows 2..N+1
LAST = N + 1
# every on-screen result is computed here
MAYA_JAN_ROWS = [i + 1 for i, (r, m, _) in enumerate(ROWS) if r == "Maya" and m == "Jan"]   # sheet-data row idx
MAYA_ROWS = [i + 1 for i, (r, _, _) in enumerate(ROWS) if r == "Maya"]
MAYA_JAN = sum(v for r, m, v in ROWS if r == "Maya" and m == "Jan")
MAYA_ALL = sum(v for r, _, v in ROWS if r == "Maya")
MANUAL = "=" + "+".join(f"C{i + 1}" for i in MAYA_JAN_ROWS)                # e.g. =C2+C5
F_FULL = f'=SUMIFS(C2:C{LAST},A2:A{LAST},"Maya",B2:B{LAST},"Jan")'
F_SUMIF = f'=SUMIF(A2:A{LAST},"Maya",C2:C{LAST})'
F_SUMIFS1 = f'=SUMIFS(C2:C{LAST},A2:A{LAST},"Maya")'
SUMR, R1, R2 = f"C2:C{LAST}", f'A2:A{LAST},"Maya"', f'B2:B{LAST},"Jan"'

CW = [240, 210, 230]
ROW_H = 80
FS = 38
SHEET_Y = 650
BAR_Y = 1300
CHIP_Y = 1505
AMBER_T = (255, 236, 196)
BLUE_T = (214, 232, 255)
GREEN_T = (210, 244, 226)
C_SUM = (40, 110, 220)
C_CRIT = (200, 120, 0)

def sheet():
    s = Sheet(0, SHEET_Y, CW, DATA, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def col_fill(c, col, rows=None):
    return {(r, c): col for r in (rows or range(1, N + 1))}

def bar(base, text, t=None, t0=0.0, colors=None, size=34, w=980, y=BAR_Y, a=1.0):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, colors=colors, size=size, a=a)

FULL_COLORS = [(SUMR, C_SUM), (R1, C_CRIT), (R2, C_CRIT)]

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "STOP", W / 2, 430, F("Bold", 190), AMBER, t, 0.0, stroke=10)
    pop_text(base, "adding by hand", W / 2, 610, F("Bold", 100), WHITE, t, 0.12, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.35:
        pill(d, W / 2, 750, "2 CONDITIONS  ·  1 FORMULA", RED, size=40, a=ease(seg(t, 0.35, 0.6)))
    p1 = ease(seg(t, 0.45, 0.8))
    bad = "=C2+C5+C9+C14+C22+C31"
    if p1 > 0:
        y = 930 + (1 - p1) * 40
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        formula_bar(lay, 70, y, 860, bad, a=p1, size=44)
        ld = ImageDraw.Draw(lay)
        x0 = 70 + 118; x1 = x0 + F("Mono", 44).getlength(bad)
        ld.line([(x0 - 6, y + 52), (x0 - 6 + (x1 - x0 + 12) * ease(seg(t, 0.75, 1.0)), y + 52)], fill=rgba(RED, p1), width=10)
        base.alpha_composite(lay)
        cross_icon(ImageDraw.Draw(base), 990, y + 52, back(seg(t, 0.9, 1.15)) * 56)
    p2 = ease(seg(t, 1.0, 1.35))
    if p2 > 0:
        y = 1130 + (1 - p2) * 40
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        formula_bar(lay, 70, y, 860, '=SUMIFS(C:C,A:A,"Maya",B:B,"Jan")', a=p2, size=36,
                    colors=[("C:C", C_SUM), ('A:A,"Maya"', C_CRIT), ('B:B,"Jan"', C_CRIT)])
        base.alpha_composite(lay)
        r = back(seg(t, 1.3, 1.6)) * 56
        if r > 2: check_icon(ImageDraw.Draw(base), 990, y + 52, r)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "THE QUESTION", AMBER, "Maya's sales\nin January?", y=290)
    s = sheet()
    fills = {}
    # walk Maya rows, then keep the Jan ones
    for k, r in enumerate(MAYA_ROWS):
        if t > 0.7 + k * 0.25: fills[(r, 0)] = AMBER_T
    if t > 1.9:
        for r in MAYA_JAN_ROWS:
            fills.update({(r, c): GREEN_T for c in range(3)})
    s.draw(base, fills=fills, font_size=FS)
    bar(base, MANUAL, t, 2.2, size=46)
    result_chip(base, W / 2, CHIP_Y, "New rows? Redo it.", False, t, 3.0)
    return base

def sc_anatomy(t, D):
    base = background()
    label_card(base, t, 0.0, "HOW IT READS", AMBER, "SUMIFS in\nplain English", y=290)
    bar(base, F_FULL, t, 0.3, size=34, y=650, colors=FULL_COLORS)
    items = [("Add up", SUMR, "(Sales)", C_SUM), ("where", f'A2:A{LAST} = "Maya"', "", C_CRIT),
             ("and", f'B2:B{LAST} = "Jan"', "", C_CRIT)]
    for i, (w1, w2, w3, col) in enumerate(items):
        p = ease(seg(t, 1.9 + i * 0.4, 2.2 + i * 0.4))
        if p <= 0: continue
        y = 870 + i * 160 + (1 - p) * 30
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([70, y - 62, W - 70, y + 62], 36, fill=rgba(NAVY2, p))
        ld.ellipse([110, y - 32, 174, y + 32], fill=rgba(col if col != C_CRIT else AMBER, p))
        ld.text((142, y + 2), str(i + 1), font=F("Bold", 40), fill=rgba(WHITE if col == C_SUM else NAVY, p), anchor="mm")
        f1 = F("Bold", 46); x = 205
        ld.text((x, y), w1, font=f1, fill=rgba(WHITE, p), anchor="lm"); x += f1.getlength(w1) + 22
        f2 = F("Mono", 40)
        ld.text((x, y), w2, font=f2, fill=rgba(BLUE if col == C_SUM else AMBER, p), anchor="lm"); x += f2.getlength(w2) + 22
        if w3: ld.text((x, y), w3, font=F("Medium", 40), fill=rgba(MUTED, p), anchor="lm")
        base.alpha_composite(lay)
    d = ImageDraw.Draw(base)
    if t > 3.4:
        pill(d, W / 2, 1380, "Sum range goes FIRST", AMBER, fg=NAVY, size=44, a=ease(seg(t, 3.4, 3.7)))
    return base

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Use SUMIFS", sub="Two conditions, one formula.")
    s = sheet()
    fills = {}
    if t > 1.0: fills.update(col_fill(2, BLUE_T))
    if t > 1.35: fills.update(col_fill(0, AMBER_T))
    if t > 1.7: fills.update(col_fill(1, AMBER_T))
    tc = {}
    if t > 2.3:
        for r in MAYA_JAN_ROWS:
            fills.update({(r, c): GREEN for c in range(3)})
            tc.update({(r, c): WHITE for c in range(3)})
    s.draw(base, fills=fills, text_cols=tc, font_size=FS)
    if t > 1.0: s.outline(base, s.col_box(2), C_SUM, a=ease(seg(t, 1.0, 1.3)))
    if t > 1.35: s.outline(base, s.col_box(0), (230, 140, 0), a=ease(seg(t, 1.35, 1.65)))
    if t > 1.7: s.outline(base, s.col_box(1), (230, 140, 0), a=ease(seg(t, 1.7, 2.0)))
    bar(base, F_FULL, t, 0.4, colors=FULL_COLORS)
    d = ImageDraw.Draw(base)
    if t > 3.3:
        parts = " + ".join(money(ROWS[r - 1][2]) for r in MAYA_JAN_ROWS)
        pill(d, W / 2, SHEET_Y - 42, parts, NAVY2, fg=AMBER, size=34, a=ease(seg(t, 3.3, 3.6)))
    result_chip(base, W / 2, CHIP_Y, money(MAYA_JAN), True, t, 2.8)
    return base

def sc_trap(t, D):
    base = background()
    label_card(base, t, 0.0, "WATCH OUT", RED, "SUMIF flips\nthe order", y=290)
    d = ImageDraw.Draw(base)
    p1 = ease(seg(t, 0.5, 0.85))
    if p1 > 0:
        bar(base, F_SUMIF, size=40, y=690 + (1 - p1) * 30, a=p1, colors=[(SUMR, C_SUM)])
    if t > 1.3:
        pill(d, W / 2, 850, "SUMIF:  sum range LAST", NAVY2, fg=BLUE, size=40, a=ease(seg(t, 1.3, 1.6)))
    p2 = ease(seg(t, 1.9, 2.25))
    if p2 > 0:
        bar(base, F_SUMIFS1, size=40, y=990 + (1 - p2) * 30, a=p2, colors=[(SUMR, C_SUM)])
    if t > 2.7:
        pill(d, W / 2, 1150, "SUMIFS:  sum range FIRST", NAVY2, fg=BLUE, size=40, a=ease(seg(t, 2.7, 3.0)))
    result_chip(base, W / 2, 1360, f"Both = {money(MAYA_ALL)}", True, t, 3.5)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=420)
    info_rows(base, t, 0.4, [("Excel 365, 2016+, web, Mac", True), ("Google Sheets", True),
                             ("Same syntax in both", True), ('Text criteria need "quotes"', None)], y0=740, step=165)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_problem", sc_problem, 4.6),
    ("03_anatomy", sc_anatomy, 5.0),
    ("04_fix", sc_fix, 6.4),
    ("05_trap", sc_trap, 5.0),
    ("06_both", sc_both, 3.6),
    ("07_outro", sc_outro, 3.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), MANUAL, F_FULL, MAYA_JAN, MAYA_ALL, MAYA_JAN_ROWS, MAYA_ROWS)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"2026-11-09-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 1.3, starts[3] + 2.8, starts[4] + 3.5])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
