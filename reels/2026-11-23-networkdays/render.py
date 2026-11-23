"""Reel: count business days between two dates with NETWORKDAYS (Excel & Google Sheets).

Common mistake: =C2-B2 gives calendar days, weekends included (Launch 12/1/26 -> 12/31/26 = 30).
=NETWORKDAYS(B2,C2) counts Mon-Fri only, start AND end day included -> 23.
Optional 3rd argument = range of holiday dates: =NETWORKDAYS(B2,C2,F2:F4) -> 22.
Syntax (Microsoft Support + Google Docs Editors Help): NETWORKDAYS(start_date, end_date, [holidays]);
weekend = Saturday + Sunday; NETWORKDAYS.INTL for other weekend days (both apps).
Inclusive counting checked against Microsoft's own example (10/1/2012-3/1/2013 = 110, 109, 107) with numpy busday_count.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> networkdays.mp4 + cover.jpg
"""
import os, sys, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "networkdays"
DATE = "2026-11-23"
TASKS = [("Launch", "2026-12-01", "2026-12-31"), ("Report", "2026-11-02", "2026-11-30"),
         ("Audit", "2027-01-04", "2027-01-29")]                                     # rows 2..4
HOLS = ["2026-11-26", "2026-12-25", "2027-01-01"]                                   # F2:F4

def d(s): return dt.date.fromisoformat(s)
def us(s): x = d(s); return f"{x.month}/{x.day}/{x.year % 100}"
def nwd(a, b, h=()): return int(np.busday_count(a, str(d(b) + dt.timedelta(days=1)), holidays=list(h)))
assert nwd("2012-10-01", "2013-03-01") == 110 and nwd("2012-10-01", "2013-03-01", ["2012-11-22"]) == 109

MINUS = [(d(b) - d(a)).days for _, a, b in TASKS]        # =C2-B2
NWD = [nwd(a, b) for _, a, b in TASKS]                   # =NETWORKDAYS(B2,C2)
NWDH = [nwd(a, b, HOLS) for _, a, b in TASKS]            # =NETWORKDAYS(B2,C2,F2:F4)
assert MINUS == [30, 28, 25] and NWD == [23, 21, 20] and NWDH == [22, 20, 20]

# December 2026 calendar (Dec 1 = Tuesday)
assert d("2026-12-01").weekday() == 1
CAL = []
day = 1
week = [""] * d("2026-12-01").weekday()
while day <= 31:
    week.append(str(day)); day += 1
    if len(week) == 7: CAL.append(week); week = []
if week: CAL.append(week + [""] * (7 - len(week)))
WEEKEND = [(r, c) for r, wk in enumerate(CAL) for c in (5, 6) if wk[c]]
assert len(WEEKEND) == 8 and 31 - len(WEEKEND) == NWD[0]

F_MINUS = "=C2-B2"
F_FIX = "=NETWORKDAYS(B2,C2)"
F_HOL = "=NETWORKDAYS(B2,C2,F2:F4)"
C_A = (200, 120, 0)
C_B = (40, 110, 220)
C_F = (150, 70, 200)
GREEN_T = (210, 244, 226)
RED_T = (255, 214, 214)
AMBER_T = (255, 236, 196)
BLUE_T = (214, 230, 255)
PURPLE_T = (236, 222, 250)
CW = [250, 220, 220, 180]
ROW_H = 84
FS = 40

def grid(y, days, row_h=ROW_H):
    data = [["Task", "Start", "End", "Days"]] + [[n, us(a), us(b), str(v) if v != "" else ""]
                                                  for (n, a, b), v in zip(TASKS, days)]
    s = Sheet(0, y, CW, data, row_h=row_h)
    s.x = (W - s.width()) // 2
    return s

def bar(base, text, y, colors=None, t=None, t0=0.0, w=960, a=1.0, cps=28):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, cps=cps, colors=colors, a=a,
                size=fit_formula_size(text, w, max_size=54))

# ---------- scenes ----------
HOOK = [f"{MINUS[0]} DAYS?", ""]
HOOK2 = [f"{NWD[0]} WORK", "DAYS!"]
HOOK_FONT = fit_font("Bold", max(HOOK + HOOK2, key=lambda x: F("Bold", 100).getlength(x)), 880, 200)
FLIP = 1.1

def sc_hook(t, D):
    base = background()
    fixed = t >= FLIP
    if not fixed:
        pop_text(base, HOOK[0], W / 2, 450, HOOK_FONT, RED, t, -0.3, stroke=10)
    else:
        pop_text(base, HOOK2[0], W / 2, 360, HOOK_FONT, GREEN, t, FLIP - 0.05, stroke=10, dur=0.25)
        pop_text(base, HOOK2[1], W / 2, 545, HOOK_FONT, AMBER, t, FLIP, stroke=10, dur=0.25)
    if fixed:
        shown = [v if t >= FLIP + k * 0.08 else MINUS[k] for k, v in enumerate(NWD)]
        s = grid(690, shown)
        f = {(k + 1, 3): GREEN_T if t >= FLIP + k * 0.08 else RED_T for k in range(3)}
        tc = {(k + 1, 3): (20, 120, 70) for k in range(3) if t >= FLIP + k * 0.08}
    else:
        s = grid(690, MINUS)
        f = {(k + 1, 3): RED_T for k in range(3) if t >= 0.2 + k * 0.08}
        tc = {(k + 1, 3): (190, 40, 50) for k in range(3) if t >= 0.2 + k * 0.08}
    s.draw(base, fills=f, text_cols=tc, font_size=FS)
    if fixed: result_chip(base, W / 2, 1300, "Weekends skipped", True, t, FLIP)
    else: result_chip(base, W / 2, 1300, "Weekends counted", False, t, -0.2)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, FLIP, 0.2, 10)

def sc_trap(t, D):
    base = background()
    label_card(base, t, 0.0, "THE TRAP", RED, "End – Start counts\nweekends", y=290)
    cal = Sheet(0, 620, [128] * 7, CAL, row_h=88, letters=["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
                row_labels=[""] * len(CAL))
    cal.x = (W - cal.width()) // 2
    f, st = {}, {}
    for k, rc in enumerate(WEEKEND):
        t0 = 0.45 + k * 0.12
        if t >= t0: f[rc] = RED_T; st[rc] = ease(seg(t, t0, t0 + 0.2))
    cal.draw(base, fills=f, font_size=FS, strike=st,
             text_cols={rc: (190, 40, 50) for rc in WEEKEND})
    result_chip(base, W / 2, 1300, f"{len(WEEKEND)} weekend days in", False, t, 1.55)
    return shake(base, t, 1.55, 0.2, 8)

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "NETWORKDAYS", y=290)
    bar(base, F_FIX, 492, colors=[("B2", C_A), ("C2", C_B)], t=t, t0=0.15, cps=34)
    t_res = 0.95
    shown = [v if t >= t_res + k * 0.12 else "" for k, v in enumerate(NWD)]
    s = grid(640, shown)
    f = {}
    if t >= 0.6:
        f.update({(r, 1): AMBER_T for r in (1, 2, 3)}); f.update({(r, 2): BLUE_T for r in (1, 2, 3)})
    f.update({(k + 1, 3): GREEN_T for k in range(3) if t >= t_res + k * 0.12})
    s.draw(base, fills=f, font_size=FS)
    oa = ease(seg(t, 0.55, 0.75)) * (1 - seg(t, 1.3, 1.5))
    if oa > 0:
        s.outline(base, s.cell_box(1, 1), C_A, a=oa, width=6); s.outline(base, s.cell_box(1, 2), C_B, a=oa, width=6)
    result_chip(base, W / 2, 1250, "Mon–Fri only", True, t, 1.55)
    return shake(base, t, 1.55, 0.2, 10)

def sc_hol(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Skip holidays too", y=290)
    bar(base, F_HOL, 492, colors=[("B2", C_A), ("C2", C_B), ("F2:F4", C_F)], t=t, t0=0.1, cps=44)
    t_res = 1.2
    shown = [NWDH[k] if t >= t_res + k * 0.12 else NWD[k] for k in range(3)]
    s = grid(625, shown, row_h=72)
    f = {}
    for k in range(3):
        if t >= t_res + k * 0.12:
            f[(k + 1, 3)] = GREEN_T if NWDH[k] == NWD[k] else AMBER_T
    s.draw(base, fills=f, font_size=FS)
    hs = Sheet(0, 1000, [260], [["Holidays"]] + [[us(h)] for h in HOLS], row_h=66, letters=["F"])
    hs.x = (W - hs.width()) // 2
    hf = {(r, 0): PURPLE_T for r in (1, 2, 3)} if t >= 0.7 else {}
    hs.draw(base, fills=hf, font_size=FS)
    hs.outline(base, hs.col_box(0), C_F, a=ease(seg(t, 0.7, 0.9)), width=6)
    result_chip(base, W / 2, 1450, "Holidays skipped", True, t, 1.65)
    return shake(base, t, 1.65, 0.2, 10)

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.3, [("Excel 2007+ & 365", True), ("Google Sheets", True),
                             ("Counts start AND end day", None), ("Other weekends: NETWORKDAYS.INTL", None)],
              y0=660, step=150, gap=0.25, size=40)
    return base

QUESTION = "By hand or formula?"

def sc_outro(t, D):
    return loop_back(outro(t, question=QUESTION), sc_hook(0.0, 2.4), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.4),
    ("02_trap", sc_trap, 2.4),
    ("03_fix", sc_fix, 2.6),
    ("04_hol", sc_hol, 2.6),
    ("05_both", sc_both, 2.3),
    ("06_outro", sc_outro, 2.8),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| minus", MINUS, "| nwd", NWD, "| hol", NWDH, "| hook font", HOOK_FONT.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, FLIP, starts[2] + 0.95])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.4).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
