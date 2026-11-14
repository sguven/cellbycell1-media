"""Reel: Highlight the whole row, not just one cell (every Excel version + Google Sheets).

Select A2:D7, conditional formatting with a custom formula =$D2>70000. The $ locks column D, so every
cell in the row checks the same salary. Trap: without the $ (=D2>70000) the reference slides right and
only column A lights up. Bonus: =$B2="Sales".

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> highlight-whole-row.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

DATE, SLUG = "2026-11-14", "highlight-whole-row"
PEOPLE = [("Maya", "Sales", "Austin", 64000), ("Jordan", "Ops", "Denver", 82500), ("Emma", "HR", "Boston", 58900),
          ("Priya", "IT", "Miami", 91200), ("Noah", "Sales", "Seattle", 69500), ("Luis", "Sales", "Chicago", 76300)]
LIMIT = 70000
def money(v): return f"${v:,.0f}"
DATA = [["Name", "Team", "City", "Salary"]] + [[n, tm, c, money(s)] for n, tm, c, s in PEOPLE]
N = len(PEOPLE)
NC = 4
def num(s): return float(s.replace("$", "").replace(",", ""))

# every highlighted cell is computed from the table with the same rule logic Excel/Sheets use
RULE = f"=$D2>{LIMIT}"
TRAP = f"=D2>{LIMIT}"
BONUS = '=$B2="Sales"'
GOOD = cf_matches(DATA, 3, lambda v: num(v) > LIMIT, NC, lock_col=True)          # whole rows
BAD = cf_matches(DATA, 3, lambda v: num(v) > LIMIT, NC, lock_col=False)          # column A only
SALES = cf_matches(DATA, 1, lambda v: v == "Sales", NC, lock_col=True)
HI_ROWS = sorted({r for r, _ in GOOD})
N_HI = len(HI_ROWS)
N_SALES = len({r for r, _ in SALES})
BAD_COLS = sorted({c for _, c in BAD})

CW = [230, 200, 230, 250]
ROW_H = 74
FS = 38
SHEET_Y = 620
MENU_Y = 1270
CHIP_Y = 1480
HI = (255, 214, 120)        # amber highlight fill
BLUE_T = (214, 232, 255)
SEL_T = (234, 241, 255)
BLUE_O = (40, 110, 220)
RED_T = (255, 214, 214)

def sheet(data=DATA, cw=CW, y=SHEET_Y, row_h=ROW_H):
    s = Sheet(0, y, cw, data, row_h=row_h)
    s.x = (W - s.width()) // 2
    return s

def range_box(s, c0, c1, r0=1, r1=N):
    a, b = s.cell_box(r0, c0), s.cell_box(r1, c1)
    return [a[0], a[1], b[2], b[3]]

# ---------- scenes ----------
HOOK = [["Name", "Team", "Salary"]] + [[n, tm, money(v)] for n, tm, _, v in (PEOPLE[1], PEOPLE[2], PEOPLE[3])]
HOOK_HI = [r for r in range(1, 4) if num(HOOK[r][2]) > LIMIT]

def sc_hook(t, D):
    base = background()
    pop_text(base, "FULL ROW", W / 2, 390, F("Bold", 170), AMBER, t, -0.15, stroke=10)
    pop_text(base, "not just 1 cell", W / 2, 555, F("Bold", 100), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 690, "1 RULE  ·  1 DOLLAR SIGN", RED, size=40, a=ease(seg(t, 0.3, 0.55)))
    p = ease(seg(t, 0.25, 0.55))
    if p > 0:
        s = sheet(HOOK, [290, 230, 300], y=800 + (1 - p) * 50, row_h=104)
        fills = {}
        if t < 1.0:       # before: only the salary cell
            fills = {(r, 2): HI for r in HOOK_HI} if t > 0.5 else {}
        else:             # after: the whole row sweeps in
            fills = sweep_fills([(r, c) for r in HOOK_HI for c in range(3)], t, 1.0, HI, col_gap=0.07, row_gap=0.1)
        s.draw(base, a=p, fills=fills, font_size=50)
        dd = ImageDraw.Draw(base)
        cx, cy = s.x + s.width() - 8, s.y + s.height() + 8
        if 0.5 < t < 1.0:
            cross_icon(dd, cx, cy, back(seg(t, 0.5, 0.75)) * 54)
        r = back(seg(t, 1.3, 1.6)) * 54
        if r > 2: check_icon(dd, cx, cy, r)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_trap(t, D):
    base = background()
    label_card(base, t, 0.0, "THE TRAP", RED, "Forgot the $?", sub="Rule on A2:D7, no dollar sign")
    t_res = 0.5 + len(TRAP) / 16 + 0.3
    s = sheet()
    fills = sweep_fills(BAD, t, t_res, RED_T) if t > t_res else {}
    s.draw(base, fills=fills, font_size=FS)
    s.outline(base, range_box(s, 0, NC - 1), BLUE_O, a=ease(seg(t, 0.2, 0.4)), width=6)
    formula_bar(base, 240, MENU_Y - 15, 600, TRAP, t=t, t0=0.5, cps=16, size=56, colors=[("D2", RED)])
    result_chip(base, W / 2, CHIP_Y, "Only column A lights up", False, t, t_res + 0.5)
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
    if t < t_tick:
        fills = {(r, c): SEL_T for r in range(1, N + 1) for c in range(NC)} if t > 0.3 else {}
    else:
        fills = sweep_fills(GOOD, t, t_tick, HI)
    s.draw(base, fills=fills, font_size=FS)
    if 0.3 < t < t_tick:
        s.outline(base, range_box(s, 0, NC - 1), BLUE_O, a=ease(seg(t, 0.3, 0.5)), width=6)
    if t < t_bar - 0.1:
        menu_path(base, t, t_menu, steps, MENU_Y + 15, size=menu_size)
    else:
        formula_bar(base, 210, MENU_Y - 15, 660, RULE, t=t, t0=t_bar, cps=18, size=56,
                    colors=[("$D2", (200, 120, 0))])
    dialog(base, t, t_dlg, dlg_title, ["Fill color"], button, y=SHEET_Y + 120, w=700, t_out=t_out, press=t_ok)
    result_chip(base, W / 2, CHIP_Y, "Whole row lights up", True, t, t_tick + 0.5)
    return base, t_tick

EXCEL = dict(tag="EXCEL", title="Select A2:D7, then:", sub="Format > Fill picks the color",
             steps=["Home", "Conditional Formatting", "New Rule", "Use a formula"],
             dlg_title="Format  >  Fill", button="OK")
SHEETS = dict(tag="GOOGLE SHEETS", title="Select A2:D7, then:", sub="Pick a fill under Formatting style",
              steps=["Format", "Conditional formatting", "Custom formula is"],
              dlg_title="Formatting style", button="Done")

def sc_excel(t, D): return rule_scene(t, **EXCEL)[0]
def sc_sheets(t, D): return rule_scene(t, **SHEETS)[0]
def tick_time(cfg): return rule_scene(0.0, **cfg)[1]

def sc_why(t, D):
    base = background()
    label_card(base, t, 0.0, "WHY THE $", AMBER, "It locks column D", sub="Write it for row 2, it adjusts per row")
    items = [("Column A checks $D2", True), ("Column B checks $D2", True), ("Column C checks $D2", True),
             ("Row 3 checks $D3 ...", None)]
    info_rows(base, t, 0.4, items, y0=740, step=160, gap=0.35, size=46)
    result_chip(base, W / 2, CHIP_Y, "$ = lock the column", True, t, 2.2)
    return base

def sc_bonus(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS", AMBER, "Match text too", sub="Same idea, any column")
    t_res = 0.5 + len(BONUS) / 18 + 0.3
    s = sheet()
    fills = sweep_fills(SALES, t, t_res, BLUE_T) if t > t_res else {}
    s.draw(base, fills=fills, font_size=FS)
    if t > 0.5: s.outline(base, s.col_box(1, 1, N), (200, 120, 0), a=ease(seg(t, 0.5, 0.7)), width=6)
    formula_bar(base, 200, MENU_Y - 15, 680, BONUS, t=t, t0=0.5, cps=18, size=54,
                colors=[("$B2", (200, 120, 0)), ('"Sales"', (20, 140, 90))])
    result_chip(base, W / 2, CHIP_Y, f"{N_SALES} Sales rows", True, t, t_res + 0.5)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=420)
    items = ["Every Excel version", "Google Sheets", "Mac: Style > Classic"]
    for i, s in enumerate(items):
        p = ease(seg(t, 0.4 + i * 0.3, 0.7 + i * 0.3))
        if p <= 0: continue
        y = 760 + i * 170
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([90, y - 62 + (1 - p) * 30, W - 90, y + 62 + (1 - p) * 30], 36, fill=rgba(NAVY2, p))
        check_icon(ld, 170, y + (1 - p) * 30, 38, a=p)
        ld.text((240, y + (1 - p) * 30), s, font=F("Bold", 46), fill=rgba(WHITE, p), anchor="lm")
        base.alpha_composite(lay)
    pop_text(base, "Excel for Mac: New Rule > Style: Classic > Use a formula", W / 2, 1300, F("Medium", 32), MUTED, t, 1.4, stroke=0)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_trap", sc_trap, 4.4),
    ("03_excel", sc_excel, round(tick_time(EXCEL) + 1.6, 2)),
    ("04_sheets", sc_sheets, round(tick_time(SHEETS) + 1.6, 2)),
    ("05_why", sc_why, 4.0),
    ("06_bonus", sc_bonus, 4.4),
    ("07_both", sc_both, 3.4),
    ("08_outro", sc_outro, 3.4),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.5, 0.95))
        print([(n, D) for n, _, D in SCENES], sum(D for *_, D in SCENES))
        print("hi rows", HI_ROWS, "bad", sorted(BAD), "sales rows", N_SALES, "hook hi", HOOK_HI)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 1.0, starts[2] + tick_time(EXCEL), starts[3] + tick_time(SHEETS)])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
