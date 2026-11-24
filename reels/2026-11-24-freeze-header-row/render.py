"""Reel: Lost your headers? Freeze the top row.

Excel (Microsoft Support "Freeze the top row" / "Freeze panes", Microsoft 365, Mac, web):
  View tab > Freeze Panes > Freeze Top Row. Excel for Mac: View tab > Freeze Top Row.
  Undo: View > Freeze Panes > Unfreeze Panes.
Google Sheets (Docs Editors Help 9060449): View > Freeze > pick how many rows (1 row). Undo: View > Freeze > No rows.
No keyboard shortcut is claimed. The table is invented sample data; nothing is computed on screen.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> freeze-header-row.mp4 + cover.jpg
"""
import os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "freeze-header-row"
DATE = "2026-11-24"

NAMES = ["Ava", "Noah", "Liam", "Mia", "Ella", "Leo", "Zoe", "Max", "Ivy", "Sam", "Kai", "Lily", "Owen", "Ruby",
         "Jack", "Nora", "Eli", "Isla", "Finn", "Cora"]
rnd = random.Random(24)
HDR = ["Rep", "Jan", "Feb", "Mar"]
ROWS = [[NAMES[i % len(NAMES)]] + [f"{rnd.randint(180, 980)}" for _ in range(3)] for i in range(80)]
AMBER_T = (255, 236, 196)
SLATE = (120, 132, 156)

# ---------- hook ----------
L1, L2 = "LOST YOUR", "HEADERS?"
F1 = fit_font("Bold", L1, 965, 190)
F2 = F1
HY = 720

def hook_top(t):            # keeps scrolling: constant motion from frame 0
    return 38 + int(t / 0.16)

def sc_hook(t, D):
    base = background()
    pop_text(base, L1, W / 2, 400, F1, AMBER, t, -0.3, stroke=10)
    pop_text(base, L2, W / 2, 590, F2, AMBER, t, -0.2, stroke=10)
    cw = [140, 110, 110]
    hdr, rows = HDR[:3], [r[:3] for r in ROWS]
    probe = Sheet(0, 0, cw, [hdr], row_labels=["99"])
    sw = probe.width(); gap = 56
    x0 = (W - 2 * sw - gap) // 2
    top = hook_top(t)
    scroll_sheet(base, x0, HY, cw, hdr, rows, top, 7, frozen=False, row_h=76, font_size=32)
    scroll_sheet(base, x0 + sw + gap, HY, cw, hdr, rows, top, 7, frozen=True, row_h=76, font_size=32,
                 header_fill=AMBER_T, divider=(SLATE, 7))
    d = ImageDraw.Draw(base)
    yb = HY + 58 + 76 * 7 + 90
    a1 = ease(seg(t, 0.0, 0.2)); a2 = ease(seg(t, 0.35, 0.6))
    for cx, s, ok, a in [(x0 + sw / 2, "Scrolled", False, a1), (x0 + sw + gap + sw / 2, "Frozen", True, a2)]:
        if a <= 0: continue
        pill(d, cx + 30, yb, s, GREEN if ok else RED, size=42, a=a)
        icx = cx + 30 - (F("Bold", 42).getlength(s) + 42 * 1.4) / 2 - 48
        (check_icon if ok else cross_icon)(d, icx, yb, 38, a=a)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, 0.35, 0.2, 10)

# ---------- big demo sheet ----------
BX_CW = [230, 170, 170, 170]
BY = 700
NV = 9

def big_x():
    return (W - Sheet(0, 0, BX_CW, [HDR], row_labels=["99"]).width()) // 2

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "SCROLLED DOWN", RED, "Which one is Feb?", y=290)
    top = int(46 * ease_io(seg(t, 0.25, 1.2)))
    s = scroll_sheet(base, big_x(), BY - 40, BX_CW, HDR, ROWS, top, NV, frozen=False)
    if t >= 1.3:
        for c in (1, 2, 3):
            cx = s.col_x(c) + BX_CW[c] / 2
            pop_text(base, "?", cx, BY - 40 + 29, F("Bold", 64), RED, t, 1.3 + 0.1 * c, stroke=8)
    return shake(base, t, 1.35, 0.25, 12)

def freeze_demo(base, t, t_freeze, divider):
    top = int(46 * ease_io(seg(t, t_freeze + 0.15, D_DEMO - 0.25)))
    on = t >= t_freeze
    flash = 0.5 + 0.5 * math.sin(t * 9) if t_freeze <= t < t_freeze + 0.5 else 1.0
    s = scroll_sheet(base, big_x(), BY, BX_CW, HDR, ROWS, top if on else 0, NV, frozen=on,
                     header_fill=AMBER_T if on else None, divider=divider if on else None)
    if on:
        s.outline(base, [s.x, s.y + s.hdr_h, s.x + s.width(), s.y + s.hdr_h + s.row_h], AMBER, a=flash, width=7)
        d = ImageDraw.Draw(base)
        r = back(seg(t, D_DEMO - 0.5, D_DEMO - 0.25)) * 40
        if r > 0: check_icon(d, s.x + s.width() - 10, s.y + s.height() + 8, r)
    return s

D_DEMO = 2.4
T_XL = 0.35 + 2 * 0.3
def sc_excel(t, D):
    base = background()
    label_card(base, t, 0.0, "EXCEL", GREEN, "Freeze Top Row", y=280)
    menu_path(base, t, 0.35, ["View", "Freeze Panes", "Freeze Top Row"], 580, size=36, gap=0.3)
    freeze_demo(base, t, T_XL + 0.15, (SLATE, 4))
    return shake(base, t, T_XL + 0.15, 0.2, 10)

T_GS = 0.35 + 2 * 0.3
def sc_sheets(t, D):
    base = background()
    label_card(base, t, 0.0, "GOOGLE SHEETS", BLUE, "Freeze 1 row", y=280)
    menu_path(base, t, 0.35, ["View", "Freeze", "1 row"], 580, size=40, gap=0.3)
    freeze_demo(base, t, T_GS + 0.15, ((150, 160, 178), 12))
    return shake(base, t, T_GS + 0.15, 0.2, 10)

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.3, [("Excel Mac: View > Freeze Top Row", True),
                             ("Undo: Unfreeze Panes / No rows", None)], y0=720, step=150, size=38)
    cw = [200, 150, 150, 150]
    x = (W - Sheet(0, 0, cw, [HDR], row_labels=["99"]).width()) // 2
    a = ease(seg(t, 0.6, 0.9))
    if a > 0:
        scroll_sheet(base, x, 1010, cw, HDR, ROWS, 10 + int(t / 0.12), 6, frozen=True, row_h=76, font_size=34,
                     header_fill=AMBER_T, divider=(SLATE, 6), a=a)
    return base

QUESTION = "Freeze it or scroll back up?"

def sc_outro(t, D):
    return loop_back(outro(t, question=QUESTION), sc_hook(0.0, 2.4), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.4),
    ("02_problem", sc_problem, 2.4),
    ("03_excel", sc_excel, D_DEMO),
    ("04_sheets", sc_sheets, D_DEMO),
    ("05_both", sc_both, 2.4),
    ("06_outro", sc_outro, 3.4),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| hook font", F1.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, starts[1] + 1.35, starts[2] + T_XL + 0.15, starts[3] + T_GS + 0.15])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.4).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
