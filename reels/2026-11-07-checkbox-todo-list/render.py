"""Reel: Checkbox to-do list that crosses itself out (Excel 365 + Google Sheets).

Insert > Checkbox, then a conditional formatting rule =$A2=TRUE with strikethrough. Bonus: COUNTIF(A2:A6,TRUE).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> checkbox-todo-list.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat

SLUG = "checkbox-todo-list"
TASKS = [("Pay rent", "Mon"), ("Book flights", "Tue"), ("Email client", "Wed"), ("Gym session", "Thu"), ("Grocery run", "Fri")]
DONE = [True, True, False, True, False]                      # final checkbox states in the demo
# computed, never typed by hand
N_DONE = sum(1 for v in DONE if v)                           # =COUNTIF(A2:A6,TRUE)
N_ALL = len(TASKS)
DONE_ROWS = [i + 1 for i, v in enumerate(DONE) if v]         # sheet rows under the header (1-based)
RULE = "=$A2=TRUE"
COUNT_F = f"=COUNTIF(A2:A{N_ALL + 1},TRUE)"

DATA = [["Done", "Task", "Due"]] + [["", a, b] for a, b in TASKS]
CW = [150, 420, 220]
ROW_H = 78
FS = 38
SHEET_Y = 620
MENU_Y = 1225
CHIP_Y = 1480
GRAY = (160, 168, 184)
AMBER_T = (255, 236, 196)
BLUE_T = (214, 232, 255)
GREEN_T = (210, 244, 226)
BLUE_O = (40, 110, 220)

def sheet(data=DATA, cw=CW, y=SHEET_Y, row_h=ROW_H, x=None):
    s = Sheet(0, y, cw, data, row_h=row_h)
    s.x = (W - s.width()) // 2 if x is None else x
    return s

def todo_state(t, ticks, rows=None, rule=True, ncol=3):
    """ticks: {row: time ticked}. Returns checks, strike, text colors for a to-do sheet at time t."""
    rows = rows if rows is not None else range(1, N_ALL + 1)
    checks, strike, cols = {}, {}, {}
    for r in rows:
        tt = ticks.get(r)
        on = ease(seg(t, tt, tt + 0.25)) if tt is not None else 0.0
        checks[(r, 0)] = on
        if rule and tt is not None:
            sp = ease(seg(t, tt + 0.2, tt + 0.5))
            for c in range(1, ncol):
                strike[(r, c)] = sp
                if sp > 0: cols[(r, c)] = GRAY
    return checks, strike, cols

def range_box(s, c0, c1, r0=1, r1=N_ALL):
    a, b = s.cell_box(r0, c0), s.cell_box(r1, c1)
    return [a[0], a[1], b[2], b[3]]

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "CHECK IT", W / 2, 390, F("Bold", 180), AMBER, t, -0.15, stroke=10)
    pop_text(base, "It crosses out", W / 2, 560, F("Bold", 100), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 690, "NO MACROS  ·  1 RULE", RED, size=40, a=ease(seg(t, 0.3, 0.55)))
    p = ease(seg(t, 0.3, 0.6))
    if p > 0:
        data = [["Done", "Task"]] + [["", a] for a, _ in TASKS[:3]]
        s = sheet(data, [150, 500], y=800 + (1 - p) * 50, row_h=112)
        ch, st, co = todo_state(t, {1: 0.65, 2: 1.05}, rows=range(1, 4), ncol=2)
        fills = {(r, c): GREEN_T for r in (1, 2) for c in range(2) if t > {1: 0.85, 2: 1.25}[r]}
        s.draw(base, a=p, checks=ch, strike=st, text_cols=co, fills=fills, font_size=50)
        r = back(seg(t, 1.4, 1.7)) * 54
        if r > 2: check_icon(ImageDraw.Draw(base), s.x + s.width() - 8, s.y + s.height() + 8, r)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_step1(t, D):
    base = background()
    label_card(base, t, 0.0, "STEP 1", AMBER, "Add checkboxes", sub="Same menu in Excel 365 & Sheets")
    s = sheet()
    fills = {(r, 0): AMBER_T for r in range(1, N_ALL + 1)} if 0.4 < t < 1.9 else {}
    checks = {}
    for r in range(1, N_ALL + 1):
        if t > 1.8 + (r - 1) * 0.08: checks[(r, 0)] = 0.0
    ticks = {1: 3.0}
    if t > 3.0: checks[(1, 0)] = ease(seg(t, 3.0, 3.25))
    s.draw(base, fills=fills, checks=checks, font_size=FS)
    if 0.4 < t: s.outline(base, range_box(s, 0, 0), (230, 140, 0), a=ease(seg(t, 0.4, 0.6)))
    if t < 2.6:
        menu_path(base, t, 0.8, ["Insert", "Checkbox"], MENU_Y, size=40)
    d = ImageDraw.Draw(base)
    if t > 2.6:
        pill(d, W / 2, MENU_Y + 20, "Empty box = FALSE", NAVY2, size=40, a=ease(seg(t, 2.6, 2.9)))
    result_chip(base, W / 2, CHIP_Y, "Checked = TRUE", True, t, 3.2)
    return base

def rule_scene(t, tag, title, sub, steps, dlg_title, button, t_menu=0.6, menu_size=34):
    base = background()
    label_card(base, t, 0.0, tag, GREEN, title, sub=sub)
    t_last = t_menu + 0.45 * (len(steps) - 1)
    t_bar = t_last + 0.7
    t_dlg = t_bar + len(RULE) / 18 + 0.35
    t_ok = t_dlg + 0.35 + 0.2 + 0.45
    t_out = t_ok + 0.25
    t_tick = t_out + 0.35
    s = sheet()
    ch, st, co = todo_state(t, {1: t_tick})
    fills = {(r, c): BLUE_T for r in range(1, N_ALL + 1) for c in (1, 2)} if 0.3 < t < t_tick else {}
    s.draw(base, fills=fills, checks=ch, strike=st, text_cols=co, font_size=FS)
    if 0.3 < t < t_tick:
        s.outline(base, range_box(s, 1, 2), BLUE_O, a=ease(seg(t, 0.3, 0.5)))
    if t < t_bar - 0.1:
        menu_path(base, t, t_menu, steps, MENU_Y + 15, size=menu_size)
    else:
        formula_bar(base, 210, MENU_Y - 15, 660, RULE, t=t, t0=t_bar, cps=18, size=56,
                    colors=[("$A2", (200, 120, 0))])
    dialog(base, t, t_dlg, dlg_title, ["Strikethrough"], button, y=SHEET_Y + 120, w=700, t_out=t_out, press=t_ok)
    result_chip(base, W / 2, CHIP_Y, "Ticked = crossed out", True, t, t_tick + 0.5)
    return base, t_tick

EXCEL = dict(tag="STEP 2 · EXCEL", title="Strike it when TRUE", sub="Select B2:C6, then:",
             steps=["Home", "Conditional Formatting", "New Rule", "Use a formula"],
             dlg_title="Format  >  Font", button="OK")
SHEETS = dict(tag="STEP 2 · GOOGLE SHEETS", title="Strike it when TRUE", sub="Select B2:C6, then:",
              steps=["Format", "Conditional formatting", "Custom formula is"],
              dlg_title="Formatting style", button="Done")

def sc_excel(t, D): return rule_scene(t, **EXCEL)[0]
def sc_sheets(t, D): return rule_scene(t, **SHEETS)[0]
def tick_time(cfg): return rule_scene(0.0, **cfg)[1]

DEMO_TICKS = {r: 0.5 + k * 0.6 for k, r in enumerate(DONE_ROWS)}
def sc_demo(t, D):
    base = background()
    label_card(base, t, 0.0, "TRY IT", AMBER, "Tick = done", sub="The $ keeps every row on column A")
    s = sheet()
    ch, st, co = todo_state(t, DEMO_TICKS)
    s.draw(base, checks=ch, strike=st, text_cols=co, font_size=FS)
    d = ImageDraw.Draw(base)
    if t > 2.4:
        pill(d, W / 2, MENU_Y + 20, f"Untick it = back to normal", NAVY2, size=40, a=ease(seg(t, 2.4, 2.7)))
    return base

def sc_bonus(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Count what's done", y=300)
    t_res = 0.4 + len(COUNT_F) / 22 + 0.3
    data = DATA + [["", "Done:", str(N_DONE) if t > t_res else ""]]
    s = sheet(data, y=SHEET_Y - 20, row_h=74)
    checks = {(r, 0): 1.0 if DONE[r - 1] else 0.0 for r in range(1, N_ALL + 1)}
    strike = {(r, c): 1.0 for r in DONE_ROWS for c in (1, 2)}
    cols = {(r, c): GRAY for r in DONE_ROWS for c in (1, 2)}
    fills = {(r, 0): AMBER_T for r in range(1, N_ALL + 1)} if t > 0.6 else {}
    if t > t_res: fills[(N_ALL + 1, 2)] = GREEN_T
    s.draw(base, checks=checks, strike=strike, text_cols=cols, fills=fills, font_size=FS)
    s.outline(base, s.cell_box(N_ALL + 1, 2), (20, 140, 90), a=ease(seg(t, 0.2, 0.4)))
    if t > 0.6: s.outline(base, range_box(s, 0, 0), (230, 140, 0), a=ease(seg(t, 0.6, 0.8)))
    formula_bar(base, 120, MENU_Y - 20, 840, COUNT_F, t=t, t0=0.4, cps=22, size=46,
                colors=[(f"A2:A{N_ALL + 1}", (200, 120, 0)), ("TRUE", (20, 140, 90))])
    result_chip(base, W / 2, CHIP_Y, f"{N_DONE} of {N_ALL} done", True, t, t_res + 0.2)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=420)
    items = ["Google Sheets", "Excel for Microsoft 365", "Same rule: =$A2=TRUE"]
    for i, s in enumerate(items):
        p = ease(seg(t, 0.4 + i * 0.3, 0.7 + i * 0.3))
        if p <= 0: continue
        y = 760 + i * 170
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([90, y - 62 + (1 - p) * 30, W - 90, y + 62 + (1 - p) * 30], 36, fill=rgba(NAVY2, p))
        check_icon(ld, 170, y + (1 - p) * 30, 38, a=p)
        ld.text((240, y + (1 - p) * 30), s, font=F("Bold", 46), fill=rgba(WHITE, p), anchor="lm")
        base.alpha_composite(lay)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_step1", sc_step1, 4.6),
    ("03_excel", sc_excel, round(tick_time(EXCEL) + 1.6, 2)),
    ("04_sheets", sc_sheets, round(tick_time(SHEETS) + 1.6, 2)),
    ("05_demo", sc_demo, 4.0),
    ("06_bonus", sc_bonus, 4.6),
    ("07_both", sc_both, 3.2),
    ("08_outro", sc_outro, 3.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.4, 0.65, 0.95))
        print([(n, D) for n, _, D in SCENES], sum(D for *_, D in SCENES), N_DONE, N_ALL, DONE_ROWS)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], seed=37,
                                   impacts=[0.0, 0.65, starts[2] + tick_time(EXCEL), starts[3] + tick_time(SHEETS)],
                                   prog=((50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)), out_wav=wav)
    print("music LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
