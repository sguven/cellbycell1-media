"""Reel: make a dropdown list in 10 seconds (Excel + Google Sheets).

Excel (Microsoft Support "Create a drop-down list" / "Create a simple drop-down list", Excel 2016-2024 & 365, Win + Mac):
  select cells > Data > Data Validation > Settings: Allow = List > Source = a range, or items typed and
  separated by commas (Done,In progress,To do) > OK. "In-cell dropdown" stays checked.
Google Sheets (Google Docs Editors Help "Create an in-cell dropdown list"):
  select cells > Insert > Dropdown (or right-click > Dropdown, or Data > Data validation > Add rule)
  > Criteria "Dropdown" > enter items (each can get a color) > Done.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> dropdown-list.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "dropdown-list"
DATE = "2026-11-18"
OPTS = ["Done", "In progress", "To do"]
CHIP = {"Done": ((210, 244, 226), (20, 120, 70)), "In progress": ((255, 236, 196), (150, 90, 0)),
        "To do": ((214, 232, 255), (30, 80, 170))}
CHIPS = [CHIP[o] for o in OPTS]
SOURCE = ",".join(OPTS)                          # what goes in Excel's Source box
TASKS = [("Invoices", "Ana"), ("Report", "Ben"), ("Budget", "Cara"), ("Slides", "Dev")]
CLEAN = ["Done", "In progress", "To do", "Done"]  # status after the fix
TYPED = ["Done", "done", "Dne", "DONE"]           # typed by hand: all meant "Done"
N_SPELL = len(set(TYPED))                          # distinct spellings shown in the problem scene
CW = [290, 220, 380]
ROW_H = 84
FS = 42
RED_T = (255, 214, 214)
GREEN_T = (210, 244, 226)

def grid(y, status):
    data = [["Task", "Owner", "Status"]] + [[a, b, s] for (a, b), s in zip(TASKS, status)]
    s = Sheet(0, y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def dd(status, rows=None):
    rows = range(1, len(status) + 1) if rows is None else rows
    return {(r, 2): CHIP.get(status[r - 1]) for r in rows}

def note(base, s, y, a):
    if a <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pill(ImageDraw.Draw(lay), W / 2, y + (1 - a) * 30, s, NAVY2, size=40, a=a)
    base.alpha_composite(lay)

def pick_anim(base, s, r, t, t_open, t_click, start_i, end_i):
    """Pointer glides inside an open dropdown from option start_i to end_i and clicks at t_click."""
    x0, y0 = dropdown_option_center(s, r, 2, start_i); x1, y1 = dropdown_option_center(s, r, 2, end_i)
    m = ease_io(seg(t, t_open + 0.15, t_click - 0.1))
    py = y0 + (y1 - y0) * m
    hover = min(range(len(OPTS)), key=lambda i: abs(dropdown_option_center(s, r, 2, i)[1] - py))
    dropdown_list(base, s, r, 2, OPTS, t, t_open, hover=hover, t_close=t_click + 0.08, chips=CHIPS)
    pointer(base, x0 + 200, py + 10, click=seg(t, t_click, t_click + 0.4))

# ---------- scenes ----------
HOOK = ["10-SECOND", "DROPDOWN"]
HOOK_FONT = fit_font("Bold", max(HOOK, key=lambda x: F("Bold", 100).getlength(x)), 960, 200)
PICK = 0.8   # hook: "Done" gets picked

def sc_hook(t, D):
    base = background()
    pop_text(base, HOOK[0], W / 2, 375, HOOK_FONT, AMBER, t, -0.45, stroke=10)
    pop_text(base, HOOK[1], W / 2, 560, HOOK_FONT, AMBER, t, -0.4, stroke=10)
    picked = t >= PICK + 0.05
    st = CLEAN[:3] + ([CLEAN[3]] if picked else [""])
    s = grid(730, st)
    fl = {(4, c): GREEN_T for c in range(2)} if picked and t < PICK + 0.6 else {}
    s.draw(base, fills=fl, font_size=FS, dropdowns=dd(st))
    s.outline(base, s.cell_box(4, 2), AMBER, width=7)
    if t < PICK + 0.3:
        pick_anim(base, s, 4, t, -0.3, PICK, 2, 0)
    result_chip(base, W / 2, 1440, "No typing. No typos.", True, t, PICK + 0.25)
    fr = punch(base, t, 0.0, 0.06, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, PICK, 0.2, 10)

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "THE PROBLEM", RED, "Typing it by hand?", y=290)
    st = [TYPED[i] if t >= 0.3 + i * 0.18 else "" for i in range(4)]
    s = grid(600, st)
    f = {(r, 2): RED_T for r in range(1, 5) if st[r - 1] and t >= 1.2}
    s.draw(base, fills=f, font_size=FS)
    result_chip(base, W / 2, 1250, f"{N_SPELL} ways to spell Done", False, t, 1.35)
    return shake(base, t, 1.35, 0.2, 10)

def sc_excel_menu(t, D):
    base = background()
    label_card(base, t, 0.0, "EXCEL", (40, 110, 220), "Select the cells", y=290)
    s = grid(560, [""] * 4)
    s.draw(base, font_size=FS)
    p = ease(seg(t, 0.25, 0.6))
    if p > 0:
        b0, b1 = s.cell_box(1, 2), s.cell_box(4, 2)
        box = [b0[0], b0[1], b1[2], b0[3] + (b1[3] - b0[3]) * p]
        s.outline(base, box, AMBER, width=8)
    menu_path(base, t, 0.8, ["Data", "Data Validation"], 1210, size=48, gap=0.5)
    return base

PANEL_Y, PANEL_W = 640, 960
OK_T = 2.25

def sc_excel_box(t, D):
    base = background()
    label_card(base, t, 0.0, "EXCEL", (40, 110, 220), "Allow: List", y=290)
    x0 = (W - PANEL_W) / 2
    p = panel(base, t, 0.05, "Data Validation", x0, PANEL_Y, PANEL_W, 520)
    if p > 0:
        form_field(base, x0 + 40, PANEL_Y + 180, PANEL_W - 80, "Allow", "List", t=t, t0=0.45, cps=30, a=p,
                   arrow=True, hot=0.3 < t < 0.9)
        form_field(base, x0 + 40, PANEL_Y + 300, PANEL_W - 80, "Source", SOURCE, t=t, t0=0.95, cps=24, a=p,
                   hot=t >= 0.9)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        bx, by = x0 + PANEL_W - 40 - 170, PANEL_Y + 440
        pr = seg(t, OK_T, OK_T + 0.3)
        d.rounded_rectangle([bx, by - 40, bx + 170, by + 40], 40, fill=rgba(GREEN if pr > 0 else (40, 110, 220), p))
        d.text((bx + 85, by), "OK", font=F("Bold", 40), fill=rgba(WHITE, p), anchor="mm")
        base.alpha_composite(lay)
        if pr > 0: pointer(base, bx + 100, by + 10, click=pr)
    note(base, "Split items with commas", 1300, ease(seg(t, 1.3, 1.6)))
    return base

def sc_sheets(t, D):
    base = background()
    label_card(base, t, 0.0, "GOOGLE SHEETS", GREEN, "Insert > Dropdown", y=290)
    x0 = (W - PANEL_W) / 2
    p = panel(base, t, 0.25, "Dropdown", x0, 600, PANEL_W, 560)
    if p > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for i, o in enumerate(OPTS):
            q = ease(seg(t, 0.5 + i * 0.3, 0.75 + i * 0.3)) * p
            if q <= 0: continue
            y = 600 + 170 + i * 120
            bg, fg = CHIPS[i]
            d.ellipse([x0 + 50, y - 30, x0 + 110, y + 30], fill=rgba(bg, q), outline=rgba(fg, q), width=4)
            d.rounded_rectangle([x0 + 140, y - 46, x0 + PANEL_W - 50, y + 46], 14, fill=rgba((244, 246, 250), q),
                                outline=rgba((190, 198, 214), q), width=3)
            d.text((x0 + 170, y), o, font=F("Medium", 42), fill=rgba((30, 40, 60), q), anchor="lm")
        base.alpha_composite(lay)
    note(base, "Each item can get a color", 1290, ease(seg(t, 1.5, 1.8)))
    return base

RES_OPEN, RES_PICK = 0.45, 1.35
def sc_result(t, D):
    base = background()
    label_card(base, t, 0.0, "RESULT", GREEN, "Click. Pick. Done.", y=290)
    st = list(CLEAN)
    if t >= RES_PICK + 0.05: st[2] = "Done"
    s = grid(560, st)
    fl = {(3, c): GREEN_T for c in range(2)} if RES_PICK + 0.05 <= t < RES_PICK + 0.6 else {}
    s.draw(base, fills=fl, font_size=FS, dropdowns=dd(st))
    if t < RES_OPEN:
        b = s.cell_box(3, 2)
        m = ease_io(seg(t, 0.0, RES_OPEN - 0.05))
        pointer(base, b[2] - 30 + (1 - m) * 160, (b[1] + b[3]) / 2 + (1 - m) * 260, click=0)
    elif t < RES_PICK + 0.3:
        pick_anim(base, s, 3, t, RES_OPEN, RES_PICK, 2, 0)
    result_chip(base, W / 2, 1300, "Same spelling every time", True, t, RES_PICK + 0.3)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.3, [("Excel 2016+ & 365, Win + Mac", True), ("Google Sheets", True),
                             ("Sheets: right-click > Dropdown", None)], y0=680, step=160, size=42)
    return base

def sc_outro(t, D):
    return loop_back(outro(t), sc_hook(0.0, 2.4), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.4),
    ("02_problem", sc_problem, 2.4),
    ("03_excel_menu", sc_excel_menu, 2.2),
    ("04_excel_box", sc_excel_box, 2.8),
    ("05_sheets", sc_sheets, 2.6),
    ("06_result", sc_result, 2.6),
    ("07_both", sc_both, 2.2),
    ("08_outro", sc_outro, 2.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.3, 0.6, 0.95))
        print(sum(D for *_, D in SCENES), "| spellings", N_SPELL, TYPED, "| source", SOURCE, "| hook font", HOOK_FONT.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, PICK, starts[5] + RES_PICK])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.4).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
