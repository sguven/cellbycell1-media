"""Reel: Insert today's date and time instantly (Excel + Google Sheets).

Ctrl+; = today's date, Ctrl+Shift+; = current time (static values, unlike =TODAY()/=NOW() which recalculate).
Date + time: Excel Ctrl+; then Space then Ctrl+Shift+; ; Google Sheets Ctrl+Alt+Shift+; . Mac in Sheets: Cmd instead of Ctrl.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> date-time-shortcuts.mp4 + cover.jpg
"""
import os, sys, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "date-time-shortcuts"
# the demo "now" (post day); every value on screen is derived from these
NOW = dt.datetime(2026, 11, 8, 17, 2)
TOMORROW = NOW + dt.timedelta(days=1)
def us_date(d): return f"{d.month}/{d.day}/{d.year}"                 # m/d/yyyy, US short date
def us_time(d): return d.strftime("%I:%M %p").lstrip("0")             # h:mm AM/PM
D_TODAY, D_TOMORROW, T_NOW = us_date(NOW), us_date(TOMORROW), us_time(NOW)
DT_NOW = f"{D_TODAY} {T_NOW}"

K_DATE = ["Ctrl", "+", ";"]
K_TIME = ["Ctrl", "+", "Shift", "+", ";"]
K_DT_XL = ["Ctrl", "+", ";", "then", "Space", "then", "Ctrl", "+", "Shift", "+", ";"]
K_DT_GS = ["Ctrl", "+", "Alt", "+", "Shift", "+", ";"]

TASKS = ["Invoice sent", "Call back", "Order shipped"]
ROW_H = 92
FS = 42
SHEET_Y = 640
KEY_Y = 1250
CHIP_Y = 1480
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)
RED_T = (255, 220, 221)
DARK_RED = (190, 40, 46)
DARK_GREEN = (20, 130, 80)

def sheet(data, cw, y=SHEET_Y, row_h=ROW_H):
    s = Sheet(0, y, cw, data, row_h=row_h)
    s.x = (W - s.width()) // 2
    return s

def day_pill(base, t, t0, text="NEXT DAY", y=KEY_Y):
    if t > t0:
        pill(ImageDraw.Draw(base), W / 2, y, text, NAVY2, size=42, a=ease(seg(t, t0, t0 + 0.25)))

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "STOP", W / 2, 380, F("Bold", 200), AMBER, t, -0.15, stroke=10)
    pop_text(base, "typing dates", W / 2, 560, F("Bold", 104), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.25:
        pill(d, W / 2, 690, "1 SHORTCUT  ·  1 SECOND", RED, size=40, a=ease(seg(t, 0.25, 0.5)))
    # bad vs good, both on screen by ~1.2 s
    for i, (y, ok, t0) in enumerate(((880, False, 0.35), (1130, True, 0.75))):
        p = ease(seg(t, t0, t0 + 0.3))
        if p <= 0: continue
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        yy = y + (1 - p) * 40
        ld.rounded_rectangle([70, yy - 100, W - 70, yy + 100], 40, fill=rgba(NAVY2, p))
        ld.rounded_rectangle([70, yy - 100, 84, yy + 100], 6, fill=rgba(GREEN if ok else RED, p))
        (check_icon if ok else cross_icon)(ld, 150, yy, 44, a=p)
        if not ok:
            ld.text((220, yy - 30), "=TODAY()", font=F("Mono", 60), fill=rgba(WHITE, p), anchor="lm")
            ld.text((220, yy + 45), "changes every day", font=F("Medium", 40), fill=rgba(MUTED, p), anchor="lm")
            q = ease(seg(t, t0 + 0.3, t0 + 0.55))
            if q > 0: ld.line([(210, yy - 20), (210 + 300 * q, yy - 20)], fill=rgba(RED, p), width=9)
        base.alpha_composite(lay)
        if ok:
            keycaps(base, t, t0 + 0.1, K_DATE, yy - 32, size=44, gap=0.18, cx=372, a=p)
            ImageDraw.Draw(base).text((220, yy + 52), f"{D_TODAY}, fixed for good", font=F("Medium", 40),
                                      fill=rgba(MUTED, p), anchor="lm")
    # mini sheet: the stamped date lands in the cell
    q = ease(seg(t, 0.9, 1.2))
    if q > 0:
        t_val = HOOK_PRESS + 0.05
        data = [["Task", "Logged"], ["Invoice sent", D_TODAY if t > t_val else ""]]
        s = sheet(data, [430, 400], y=1330 + (1 - q) * 40, row_h=84)
        s.draw(base, a=q, font_size=FS, fills={(1, 1): GREEN_T if t > t_val else AMBER_T})
        s.outline(base, s.cell_box(1, 1), (20, 140, 90) if t > t_val else (230, 140, 0), a=q)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)
HOOK_PRESS = 0.75 + 0.1 + 0.18

def sc_trap(t, D):
    base = background()
    label_card(base, t, 0.0, "THE TRAP", RED, "=TODAY() won't stay put", sub="Great for 'today', bad for a log")
    t_flip = 2.0
    flipped = t > t_flip
    shown = D_TOMORROW if flipped else D_TODAY
    data = [["Task", "Logged"]] + [[x, shown] for x in TASKS]
    s = sheet(data, [430, 400])
    fills, cols = {}, {}
    if 0.4 < t < t_flip: fills = {(r, 1): AMBER_T for r in range(1, 4)}
    if flipped:
        fills = {(r, 1): RED_T for r in range(1, 4)}; cols = {(r, 1): DARK_RED for r in range(1, 4)}
    s.draw(base, fills=fills, text_cols=cols, font_size=FS)
    if 0.4 < t < t_flip:
        s.outline(base, s.col_box(1), (230, 140, 0), a=ease(seg(t, 0.4, 0.6)))
    if 0.4 < t < t_flip - 0.3:
        formula_bar(base, 210, KEY_Y - 52, 660, "=TODAY()", size=56)
    day_pill(base, t, t_flip - 0.3, f"NEXT DAY  ·  {D_TOMORROW}")
    result_chip(base, W / 2, CHIP_Y, "Every row changed", False, t, t_flip + 0.4)
    return base

def fix_scene(t, tag, title, sub, keys, data, col, value, chip, cw, key_size=48, next_day=False):
    base = background()
    label_card(base, t, 0.0, tag, GREEN, title, sub=sub)
    t_press = keycaps(base, t, 0.7, keys, KEY_Y, size=key_size, gap=0.22)
    t_val = t_press + 0.15
    data = [list(r) for r in data]
    if t > t_val: data[1][col] = value
    s = sheet(data, list(cw))
    fills = {(1, col): GREEN_T} if t > t_val else {(1, col): AMBER_T}
    s.draw(base, fills=fills, font_size=FS, text_cols={(1, col): (30, 40, 60)})
    s.outline(base, s.cell_box(1, col), (20, 140, 90) if t > t_val else (230, 140, 0), a=ease(seg(t, 0.3, 0.5)))
    if next_day:
        day_pill(base, t, t_val + 0.6, f"NEXT DAY  ·  {D_TOMORROW}", y=KEY_Y + 120)
        result_chip(base, W / 2, CHIP_Y + 20, chip, True, t, t_val + 1.1)
    else:
        result_chip(base, W / 2, CHIP_Y, chip, True, t, t_val + 0.35)
    return base, t_val

DATE_CFG = dict(tag="STEP 1 · DATE", title="Ctrl + ;", sub="Today's date as a fixed value", keys=K_DATE,
                data=[["Task", "Logged"]] + [[x, ""] for x in TASKS], col=1, value=D_TODAY, cw=(430, 400),
                chip=f"Still {D_TODAY}", next_day=True)
TIME_CFG = dict(tag="STEP 2 · TIME", title="Ctrl + Shift + ;", sub="The current time, also fixed", keys=K_TIME,
                data=[["Task", "Date", "Time"], [TASKS[0], D_TODAY, ""], [TASKS[1], "", ""], [TASKS[2], "", ""]],
                col=2, value=T_NOW, cw=(370, 290, 270), chip="Timestamp done")
def sc_date(t, D): return fix_scene(t, **DATE_CFG)[0]
def sc_time(t, D): return fix_scene(t, **TIME_CFG)[0]
def val_time(cfg): return fix_scene(0.0, **cfg)[1]

def sc_both_keys(t, D):
    base = background()
    label_card(base, t, 0.0, "BONUS · DATE + TIME", AMBER, "Both in one cell", sub="The keys differ here:")
    d = ImageDraw.Draw(base)
    y1, y2 = 820, 1080
    a1 = ease(seg(t, 0.4, 0.65)); a2 = ease(seg(t, 2.3, 2.55))
    if a1 > 0: d.text((W / 2, y1 - 95), "EXCEL", font=F("Bold", 40), fill=rgba(AMBER, a1), anchor="mm")
    t1 = keycaps(base, t, 0.6, K_DT_XL, y1, size=32, gap=0.2)
    if a2 > 0: ImageDraw.Draw(base).text((W / 2, y2 - 95), "GOOGLE SHEETS", font=F("Bold", 40), fill=rgba(AMBER, a2), anchor="mm")
    t2 = keycaps(base, t, 2.5, K_DT_GS, y2, size=40, gap=0.2)
    t_val = t2 + 0.2
    data = [["Logged"], [DT_NOW if t > t_val else ""]]
    s = sheet(data, [620], y=1290, row_h=90)
    s.draw(base, fills={(1, 0): GREEN_T if t > t_val else AMBER_T}, font_size=FS)
    s.outline(base, s.cell_box(1, 0), (20, 140, 90) if t > t_val else (230, 140, 0), a=ease(seg(t, 0.3, 0.5)))
    return base

def both_val_time(): return 2.5 + 3 * 0.2 + 0.2

def sc_works(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=380)
    info_rows(base, t, 0.4, [
        ("Ctrl+;  and  Ctrl+Shift+;  in both", True),
        ("Mac in Sheets: Cmd, not Ctrl", None),
        ("Want it live? =TODAY() / =NOW()", None),
    ], y0=760, step=170, size=44)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_trap", sc_trap, 4.4),
    ("03_date", sc_date, round(val_time(DATE_CFG) + 2.9, 2)),
    ("04_time", sc_time, round(val_time(TIME_CFG) + 2.4, 2)),
    ("05_both", sc_both_keys, round(both_val_time() + 1.8, 2)),
    ("06_works", sc_works, 4.0),
    ("07_outro", sc_outro, 3.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.4, 0.65, 0.95))
        print([(n, D) for n, _, D in SCENES], sum(D for *_, D in SCENES), D_TODAY, D_TOMORROW, T_NOW, DT_NOW)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"2026-11-08-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 0.75, starts[1] + 2.0, starts[2] + val_time(DATE_CFG),
                                            starts[3] + val_time(TIME_CFG), starts[4] + both_val_time()])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
