"""Reel: Duplicates gone in seconds (Remove Duplicates in Excel + Google Sheets, bonus UNIQUE).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> remove-duplicates.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat

SLUG = "remove-duplicates"
ROWS = [("Maya Chen", "Austin", 120), ("Liam Ortiz", "Denver", 85), ("Maya Chen", "Austin", 120),
        ("Ava Patel", "Boston", 64), ("Noah Kim", "Seattle", 92), ("Liam Ortiz", "Denver", 85)]
# computed from ROWS, never typed by hand
UNIQ = []
for r in ROWS:
    if r not in UNIQ: UNIQ.append(r)
DUP_IDX = [i + 1 for i, r in enumerate(ROWS) if r in ROWS[:i]]          # sheet data rows (1-based under header)
REMOVED, LEFT = len(ROWS) - len(UNIQ), len(UNIQ)
TOT_DUP, TOT_OK = sum(r[2] for r in ROWS), sum(r[2] for r in UNIQ)
NAMES = []
for r in ROWS:
    if r[0] not in NAMES: NAMES.append(r[0])

def fmt(rows): return [["Name", "City", "Order"]] + [[a, b, f"${c}"] for a, b, c in rows]
DATA, CLEAN = fmt(ROWS), fmt(UNIQ)
CW = [300, 250, 200]
ROW_H = 76
FS = 36
SHEET_Y = 640
MENU_Y = 1310
CHIP_Y = 1470
AMBER_T = (255, 236, 196)
BLUE_T = (214, 232, 255)
RED_T = (255, 214, 214)
GREEN_T = (210, 244, 226)

def sheet(data=DATA, cw=CW, y=SHEET_Y, row_h=ROW_H, letters=None, x=None):
    s = Sheet(0, y, cw, data, row_h=row_h, letters=letters)
    s.x = (W - s.width()) // 2 if x is None else x
    return s

def row_fill(rows, col, ncol=3):
    return {(r, c): col for r in rows for c in range(ncol)}

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "DUPES?", W / 2, 400, F("Bold", 200), AMBER, t, 0.0, stroke=10)
    pop_text(base, "Gone in seconds", W / 2, 570, F("Bold", 100), WHITE, t, 0.12, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 700, "BEFORE  ->  AFTER", RED, size=40, a=ease(seg(t, 0.3, 0.55)))
    names_b = [["Name"]] + [[r[0]] for r in ROWS]
    names_a = [["Name"]] + [[n] for n in NAMES]
    p1 = ease(seg(t, 0.35, 0.7))
    if p1 > 0:
        sb = sheet(names_b, [310], y=800 + (1 - p1) * 50, row_h=72, x=80)
        fills = row_fill(DUP_IDX, RED_T, 1) if t > 0.7 else {}
        sb.draw(base, a=p1, fills=fills, font_size=34)
        if t > 0.8: strike_rows(base, sb, DUP_IDX, t, 0.8)
    pa = ease(seg(t, 0.85, 1.05))
    if pa > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        arrow(ImageDraw.Draw(lay), 480, 1050, 480 + 120 * pa, 1050, AMBER, width=14, head=36)
        base.alpha_composite(lay)
    p2 = ease(seg(t, 1.0, 1.3))
    if p2 > 0:
        sa = sheet(names_a, [310], y=800 + (1 - p2) * 50, row_h=72, x=626)
        sa.draw(base, a=p2, fills=row_fill(range(1, len(names_a)), GREEN_T, 1), font_size=34)
        r = back(seg(t, 1.25, 1.55)) * 52
        if r > 2: check_icon(ImageDraw.Draw(base), 626 + sa.width() - 10, 800 + sa.height() + 10, r)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "THE PROBLEM", RED, "Same row, twice", sub="Now every total is wrong.")
    s = sheet()
    fills = {}
    for k, r in enumerate(DUP_IDX):
        if t > 0.9 + k * 0.5:
            fills.update(row_fill([r], RED_T))
            src = ROWS.index(ROWS[r - 1]) + 1
            fills.update(row_fill([src], AMBER_T))
    s.draw(base, fills=fills, font_size=FS)
    d = ImageDraw.Draw(base)
    if t > 2.0:
        pill(d, W / 2, MENU_Y, f"Total says ${TOT_DUP}", NAVY2, fg=WHITE, size=40, a=ease(seg(t, 2.0, 2.3)))
    result_chip(base, W / 2, CHIP_Y, f"Real total: ${TOT_OK}", False, t, 2.7)
    return base

def fix_scene(t, tag, title, sub, steps, dlg_title, items, button, t_menu=0.6):
    base = background()
    label_card(base, t, 0.0, tag, GREEN, title, sub=sub)
    t_dlg = t_menu + 0.45 * (len(steps) - 1) + 0.55
    t_ok = t_dlg + 0.45 + 0.2 * len(items) + 0.3
    t_out = t_ok + 0.25
    t_red, t_clean = t_out + 0.25, t_out + 0.85
    if t < t_clean:
        s = sheet()
        fills = row_fill(range(1, len(DATA)), BLUE_T) if t_menu - 0.2 < t < t_red else {}
        if t > t_red: fills = row_fill(DUP_IDX, RED_T)
        s.draw(base, fills=fills, font_size=FS)
        if t_menu - 0.2 < t < t_red:
            s.outline(base, [s.cell_box(0, 0)[0], s.cell_box(0, 0)[1], s.cell_box(len(DATA) - 1, 2)[2],
                             s.cell_box(len(DATA) - 1, 2)[3]], (40, 110, 220), a=ease(seg(t, t_menu - 0.2, t_menu)))
        strike_rows(base, s, DUP_IDX, t, t_red + 0.15)
    else:
        s = sheet(CLEAN)
        g = 1 - seg(t, t_clean + 0.6, t_clean + 1.2)
        s.draw(base, fills=row_fill(range(1, len(CLEAN)), GREEN_T) if g > 0 else {}, font_size=FS)
    hgt = 130 + len(items) * 84 + 150
    dialog(base, t, t_dlg, dlg_title, items, button, y=int(SHEET_Y + 295 - hgt / 2), t_out=t_out, press=t_ok)
    if t < t_out + 0.3:
        menu_path(base, t, t_menu, steps, MENU_Y, size=34)
    result_chip(base, W / 2, CHIP_Y, f"{REMOVED} removed  ·  {LEFT} left", True, t, t_clean + 0.2)
    return base

EXCEL = dict(tag="EXCEL", title="Remove Duplicates", sub="Data tab  >  Remove Duplicates", steps=["Data", "Remove Duplicates"],
             dlg_title="Columns to check", items=["Name", "City", "Order"], button="OK")
SHEETS = dict(tag="GOOGLE SHEETS", title="Remove duplicates", sub="Data  >  Data cleanup", steps=["Data", "Data cleanup", "Remove duplicates"],
              dlg_title="Remove duplicates", items=["Data has header row", "Name", "City", "Order"],
              button="Remove duplicates")

def _times(cfg, t_menu=0.6):
    t_dlg = t_menu + 0.45 * (len(cfg["steps"]) - 1) + 0.55
    t_ok = t_dlg + 0.45 + 0.2 * len(cfg["items"]) + 0.3
    return t_ok + 0.25 + 0.85   # t_clean

def sc_excel(t, D): return fix_scene(t, **EXCEL)
def sc_sheets(t, D): return fix_scene(t, **SHEETS)

def sc_heads(t, D):
    base = background()
    label_card(base, t, 0.0, "HEADS UP", RED, "It deletes\nwhole rows", y=320)
    items = [("Only checks the columns you tick", True), ("Copy your data first", True),
             ("Undo: Ctrl+Z  (Cmd+Z on Mac)", True)]
    for i, (s, ok) in enumerate(items):
        p = ease(seg(t, 0.5 + i * 0.35, 0.8 + i * 0.35))
        if p <= 0: continue
        y = 800 + i * 170
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([90, y - 62 + (1 - p) * 30, W - 90, y + 62 + (1 - p) * 30], 36, fill=rgba(NAVY2, p))
        check_icon(ld, 165, y + (1 - p) * 30, 36, col=AMBER, a=p)
        ld.text((225, y + (1 - p) * 30), s, font=F("Bold", 42), fill=rgba(WHITE, p), anchor="lm")
        base.alpha_composite(lay)
    return base

U_CW = [300, 90, 300]
def sc_bonus(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Keep the original?\nUse UNIQUE", y=280)
    n_spill = int(clamp((t - 1.9) / 0.15, 0, len(NAMES)))
    data = [["Name", "", "Unique"]] + [[r[0], "", NAMES[i] if i < n_spill else ""] for i, r in enumerate(ROWS)]
    s = sheet(data, U_CW, y=SHEET_Y - 10)
    fills = {}
    if t > 1.2: fills.update({(r, 0): AMBER_T for r in range(1, len(data))})
    fills.update({(r + 1, 2): GREEN_T for r in range(n_spill)})
    s.draw(base, fills=fills, font_size=FS)
    s.outline(base, s.cell_box(1, 2), (20, 140, 90), a=ease(seg(t, 0.2, 0.5)))
    if t > 1.2: s.outline(base, s.col_box(0, 1, len(data) - 1), (230, 140, 0), a=ease(seg(t, 1.2, 1.5)))
    formula_bar(base, 180, MENU_Y - 30, 720, "=UNIQUE(A2:A7)", t=t, t0=0.4, size=48,
                colors=[("A2:A7", (200, 120, 0))])
    result_chip(base, W / 2, CHIP_Y, f"{len(NAMES)} names · original kept", True, t, 2.7)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=420)
    items = ["Excel (Windows & Mac)", "Google Sheets", "UNIQUE: Excel 365/2021+"]
    for i, s in enumerate(items):
        p = ease(seg(t, 0.4 + i * 0.3, 0.7 + i * 0.3))
        if p <= 0: continue
        y = 760 + i * 170
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([110, y - 62 + (1 - p) * 30, W - 110, y + 62 + (1 - p) * 30], 36, fill=rgba(NAVY2, p))
        check_icon(ld, 190, y + (1 - p) * 30, 38, a=p)
        ld.text((260, y + (1 - p) * 30), s, font=F("Bold", 48), fill=rgba(WHITE, p), anchor="lm")
        base.alpha_composite(lay)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_problem", sc_problem, 4.2),
    ("03_excel", sc_excel, round(_times(EXCEL) + 1.6, 2)),
    ("04_sheets", sc_sheets, round(_times(SHEETS) + 1.5, 2)),
    ("05_heads", sc_heads, 4.0),
    ("06_bonus", sc_bonus, 5.0),
    ("07_both", sc_both, 3.0),
    ("08_outro", sc_outro, 3.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.35, 0.6, 0.95))
        print([(n, D) for n, _, D in SCENES], sum(D for *_, D in SCENES), DUP_IDX, REMOVED, LEFT, TOT_DUP, TOT_OK)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], seed=23,
                                   impacts=[0.0, 1.0, starts[2] + _times(EXCEL), starts[3] + _times(SHEETS)],
                                   prog=((52, 55, 59), (48, 52, 55), (55, 59, 62), (50, 54, 57)), out_wav=wav)
    print("music LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
