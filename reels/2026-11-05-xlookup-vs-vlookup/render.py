"""Reel: Stop using VLOOKUP (3 problems, 1 fix: XLOOKUP).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> xlookup-vs-vlookup.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat

SLUG = "xlookup-vs-vlookup"
DATA = [["Name", "ID", "Dept", "Salary"],
        ["Maya Chen", "1042", "Sales", "$64,000"],
        ["Liam Ortiz", "1057", "Finance", "$72,000"],
        ["Ava Patel", "1063", "Marketing", "$68,000"],
        ["Noah Kim", "1078", "Ops", "$59,000"]]
CW = [245, 135, 215, 190]
ROW_H = 84
FS = 35
SHEET_Y = 700
BAR_Y = 1222
CHIP_Y = 1450
AMBER_T = (255, 236, 196)
BLUE_T = (214, 232, 255)
RED_T = (255, 214, 214)
GREEN_T = (210, 244, 226)

def sheet(cw=CW, data=DATA, letters=None):
    s = Sheet(0, SHEET_Y, cw, data, row_h=ROW_H, letters=letters)
    s.x = (W - s.width()) // 2
    return s

def col_fill(c, col, rows=range(1, 5)):
    return {(r, c): col for r in rows}

def bar(base, text, t=None, t0=0.0, colors=None, size=44, w=960):
    formula_bar(base, (W - w) // 2, BAR_Y, w, text, t=t, t0=t0, colors=colors, size=size)

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "STOP", W / 2, 430, F("Bold", 190), AMBER, t, 0.0, stroke=10)
    pop_text(base, "using VLOOKUP", W / 2, 610, F("Bold", 104), WHITE, t, 0.12, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.35:
        pill(d, W / 2, 750, "3 PROBLEMS  ·  1 FIX", RED, size=40, a=ease(seg(t, 0.35, 0.6)))
    # bad vs good formulas
    p1 = ease(seg(t, 0.5, 0.85))
    if p1 > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        formula_bar(lay, 90, 930 + (1 - p1) * 40, 900, "=VLOOKUP(A2,B:D,3,FALSE)", a=p1, size=44)
        ld = ImageDraw.Draw(lay)
        ld.line([(210, 982 + (1 - p1) * 40), (210 + 720 * ease(seg(t, 0.8, 1.1)), 982 + (1 - p1) * 40)], fill=rgba(RED, p1), width=10)
        base.alpha_composite(lay)
        cross_icon(ImageDraw.Draw(base), 990, 930 + 52, 56, a=ease(seg(t, 0.95, 1.2)))
    p2 = ease(seg(t, 1.1, 1.45))
    if p2 > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        formula_bar(lay, 90, 1130 + (1 - p2) * 40, 900, "=XLOOKUP(A2,B:B,D:D)", a=p2, size=44,
                    colors=[("B:B", (200, 120, 0)), ("D:D", (40, 110, 220))])
        base.alpha_composite(lay)
        r = back(seg(t, 1.4, 1.75)) * 56
        if r > 2: check_icon(ImageDraw.Draw(base), 990, 1130 + 52, r)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_p1(t, D):
    base = background()
    label_card(base, t, 0.0, "PROBLEM 1", RED, "It can't look left", sub="You have the ID. You need the Name.")
    s = sheet()
    fills = {}
    if t > 0.5: fills.update(col_fill(1, AMBER_T))
    if t > 1.0: fills[(3, 1)] = AMBER
    if t > 1.9: fills.update(col_fill(0, RED_T))
    s.draw(base, fills=fills, font_size=FS)
    d = ImageDraw.Draw(base)
    b = s.cell_box(3, 1); a = s.cell_box(3, 0)
    p = ease(seg(t, 1.2, 1.8))
    yA = SHEET_Y - 48
    xb = (b[0] + b[2]) / 2; xa = (a[0] + a[2]) / 2
    if p > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        arrow(ld, xb, yA, xb - (xb - xa) * p, yA, RED, width=12, head=34)
        base.alpha_composite(lay)
    if t > 1.9:
        cross_icon(ImageDraw.Draw(base), (xa + xb) / 2, yA, back(seg(t, 1.9, 2.2)) * 40)
    bar(base, "=VLOOKUP(1063,B2:D5, ...)", t, 0.6, size=44)
    result_chip(base, W / 2, CHIP_Y, "Only looks RIGHT", False, t, 2.4)
    return base

def sc_p2(t, D):
    base = background()
    label_card(base, t, 0.0, "PROBLEM 2", RED, "Insert a column,\nit breaks", y=280)
    ins = ease_io(seg(t, 2.1, 2.8))
    if ins <= 0:
        s = sheet()
        fills = col_fill(3, AMBER_T); fills[(2, 3)] = AMBER
        s.draw(base, fills=fills, font_size=FS)
        bar(base, "=VLOOKUP(1057,B2:D5,3,FALSE)", t, 0.5, size=40,
            colors=[("B2:D5", (200, 120, 0)), (",3,", (200, 40, 40))])
        result_chip(base, W / 2, CHIP_Y, "$72,000", True, t, 1.4)
    else:
        data = [[r[0], r[1], ("Start" if i == 0 else ["", "Mar 2", "Jun 9", "Jan 15", "Sep 4"][i]) if ins > 0.85 else "", r[2], r[3]]
                for i, r in enumerate(DATA)]
        cw = [CW[0], CW[1], max(1, int(150 * ins)), CW[2], CW[3]]
        s = sheet(cw, data, letters=list("ABCDE"))
        fills = col_fill(2, GREEN_T) if ins > 0.2 else {}
        if t > 3.0:
            fills.update(col_fill(3, RED_T)); fills[(2, 3)] = RED
        tc = {(2, 3): WHITE} if t > 3.0 else {}
        s.draw(base, fills=fills, text_cols=tc, font_size=FS)
        bar(base, "=VLOOKUP(1057,B2:E5,3,FALSE)", size=40,
            colors=[("B2:E5", (200, 120, 0)), (",3,", (200, 40, 40))])
        result_chip(base, W / 2, CHIP_Y, "Finance  (not salary!)", False, t, 3.1)
        if 2.1 < t < 3.4:
            d = ImageDraw.Draw(base)
            pill(d, W / 2, SHEET_Y - 40, "+ NEW COLUMN", GREEN, size=34, a=ease(seg(t, 2.1, 2.4)) * (1 - seg(t, 3.1, 3.4)))
    return base

def sc_p3(t, D):
    base = background()
    label_card(base, t, 0.0, "PROBLEM 3", RED, "Forget FALSE =\nwrong answer", y=280)
    s = sheet()
    fills = {}
    if t > 2.2: fills = {(2, c): RED_T for c in range(4)}; fills[(2, 3)] = RED
    s.draw(base, fills=fills, text_cols={(2, 3): WHITE} if t > 2.2 else {}, font_size=FS)
    bar(base, "=VLOOKUP(1060,B2:D5,3)", t, 0.4, size=44, colors=[("1060", (200, 40, 40))])
    d = ImageDraw.Draw(base)
    if t > 1.4:
        pill(d, W / 2, SHEET_Y - 40, "ID 1060 doesn't exist", NAVY2, fg=AMBER, size=34, a=ease(seg(t, 1.4, 1.7)))
    result_chip(base, W / 2, CHIP_Y, "$72,000 ?!  No error", False, t, 2.3)
    return base

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Use XLOOKUP", sub="Looks left. Exact match by default.")
    s = sheet()
    fills = {}
    if t > 1.0: fills.update(col_fill(1, AMBER_T))
    if t > 1.6: fills.update(col_fill(0, BLUE_T))
    if t > 2.4: fills[(3, 1)] = AMBER; fills[(3, 0)] = GREEN
    s.draw(base, fills=fills, text_cols={(3, 0): WHITE} if t > 2.4 else {}, font_size=FS)
    if t > 1.0: s.outline(base, s.col_box(1), (230, 140, 0), a=ease(seg(t, 1.0, 1.3)))
    if t > 1.6: s.outline(base, s.col_box(0), (40, 110, 220), a=ease(seg(t, 1.6, 1.9)))
    bar(base, "=XLOOKUP(1063,B2:B5,A2:A5)", t, 0.4, size=44,
        colors=[("B2:B5", (200, 120, 0)), ("A2:A5", (40, 110, 220))])
    d = ImageDraw.Draw(base)
    if t > 1.0:
        a1 = ease(seg(t, 1.0, 1.3)); a2 = ease(seg(t, 1.6, 1.9))
        pill(d, 400, 1372, "search here", (230, 140, 0), size=30, a=a1)
        pill(d, 700, 1372, "return this", (40, 110, 220), size=30, a=a2)
    result_chip(base, W / 2, CHIP_Y + 30, "Ava Patel", True, t, 2.9)
    return base

def sc_bonus(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Add a \"not found\"\nmessage", y=280)
    s = sheet()
    s.draw(base, font_size=FS)
    bar(base, '=XLOOKUP(1060,B2:B5,A2:A5,"Not found")', t, 0.4, size=34,
        colors=[('"Not found"', (20, 140, 90))])
    result_chip(base, W / 2, CHIP_Y, "Not found  (no fake match)", True, t, 2.2)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=420)
    d = ImageDraw.Draw(base)
    items = ["Excel 365 / 2021 and newer", "Google Sheets", "Same syntax in both"]
    for i, s in enumerate(items):
        p = ease(seg(t, 0.4 + i * 0.3, 0.7 + i * 0.3))
        if p <= 0: continue
        y = 760 + i * 170
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([110, y - 62 + (1 - p) * 30, W - 110, y + 62 + (1 - p) * 30], 36, fill=rgba(NAVY2, p))
        check_icon(ld, 190, y + (1 - p) * 30, 38, a=p)
        ld.text((260, y + (1 - p) * 30), s, font=F("Bold", 50), fill=rgba(WHITE, p), anchor="lm")
        base.alpha_composite(lay)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_p1", sc_p1, 4.6),
    ("03_p2", sc_p2, 5.4),
    ("04_p3", sc_p3, 4.8),
    ("05_fix", sc_fix, 6.2),
    ("06_bonus", sc_bonus, 4.4),
    ("07_both", sc_both, 3.0),
    ("08_outro", sc_outro, 3.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        stills(SCENES, os.path.join(HERE, "stills"))
        sys.exit()
    starts, total = scene_starts(SCENES)
    fix_start = starts[4]
    wav = os.path.join(HERE, "music.wav")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], impacts=[0.0, fix_start + 2.9], out_wav=wav)
    print("music LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
