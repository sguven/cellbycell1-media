"""Reel: Stop pressing Ctrl+V - paste values only.

Google Sheets (Docs Editors Help, keyboard shortcuts): "Paste values only" = Ctrl+Shift+V (PC / Chrome OS),
Cmd+Shift+V (Mac).
Excel for Windows (Microsoft 365 Insider blog): Ctrl+Alt+V opens Paste Special, choose Values (V), Enter.
Plain Ctrl+V pastes the formula with relative references: C2 =A2*B2 pasted into A2 of another sheet shifts both
references 2 columns left, off the sheet -> #REF!. Paste values pastes the computed numbers (computed below).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> paste-values.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "paste-values"
DATE = "2026-11-20"
ROWS = [(4, 25), (3, 40), (6, 15), (2, 55)]            # A2:B5 Qty, Price;  C = A*B
TOTALS = [q * p for q, p in ROWS]
assert TOTALS == [100, 120, 90, 110]
# relative refs of =A2*B2 shifted from column C to column A move 2 columns left -> before column A -> #REF!
assert ord("A") - 2 < ord("A")
N = len(ROWS)
VALS = [f"${v}" for v in TOTALS]
BAD = ["#REF!"] * N

GREEN_T = (210, 244, 226)
RED_T = (253, 222, 222)
AMBER_T = (255, 236, 196)
C_BAD = (200, 40, 50)

def staggered(t, t0, step=0.09):
    return int(clamp((t - t0) / step + 1, 0, N)) if t >= t0 else 0

# ---------- hook ----------
L1, L2 = "STOP", "CTRL+V"
F1 = fit_font("Bold", L2, 900, 200)
F2 = fit_font("Bold", L2, 900, 200)
FILL_T = 0.55

def mini(x, y, vals, k, ok):
    data = [["Total"]] + [[vals[i] if i < k else ""] for i in range(N)]
    s = Sheet(x, y, [250], data, row_h=88)
    fills, tc = {}, {}
    for i in range(k):
        fills[(i + 1, 0)] = GREEN_T if ok else RED_T
        if not ok: tc[(i + 1, 0)] = C_BAD
    return s, fills, tc

def sc_hook(t, D):
    base = background()
    pop_text(base, L1, W / 2, 395, F1, AMBER, t, -0.3, stroke=10)
    pop_text(base, L2, W / 2, 600, F2, AMBER, t, -0.2, stroke=10)
    gap = 110; sw = 64 + 250
    x0 = (W - 2 * sw - gap) // 2
    bad, fb, tb = mini(x0, 760, BAD, N, False)
    good, fg, tg = mini(x0 + sw + gap, 760, VALS, staggered(t, FILL_T), True)
    bad.draw(base, fills=fb, text_cols=tb, font_size=44)
    good.draw(base, fills=fg, font_size=44)
    d = ImageDraw.Draw(base)
    yb = 760 + bad.height() + 90
    a1 = ease(seg(t, 0.0, 0.25)); a2 = ease(seg(t, FILL_T + 0.35, FILL_T + 0.6))
    for cx, s, col, ok, a in [(x0 + sw / 2, "Ctrl+V", RED, False, a1), (x0 + sw + gap + sw / 2, "Values", GREEN, True, a2)]:
        if a <= 0: continue
        pill(d, cx + 30, yb, s, col, size=44, a=a)
        icx = cx + 30 - (F("Bold", 44).getlength(s) + 44 * 1.4) / 2 - 50
        (check_icon if ok else cross_icon)(d, icx, yb, 40, a=a)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, FILL_T + 0.35, 0.2, 10)

# ---------- demo scenes: Data sheet -> Report sheet ----------
SY = 640
def sheets(report_vals, k, ok, copy_a=1.0):
    data = [["Qty", "Price", "Total"]] + [[str(q), f"${p}", f"${v}"] for (q, p), v in zip(ROWS, TOTALS)]
    src = Sheet(0, SY, [130, 150, 170], data, row_h=84)
    rep = [["Total"]] + [[report_vals[i] if i < k else ""] for i in range(N)]
    out = Sheet(0, SY, [210], rep, row_h=84)
    gap = 90
    src.x = (W - src.width() - out.width() - gap) // 2
    out.x = src.x + src.width() + gap
    return src, out

def demo(base, t, report_vals, t_fill, ok, sheets_a=1.0):
    k = staggered(t, t_fill)
    src, out = sheets(report_vals, k, ok)
    src.draw(base, font_size=40, fills={(r, 2): AMBER_T for r in range(1, N + 1)})
    fills = {(i + 1, 0): (GREEN_T if ok else RED_T) for i in range(k)}
    tc = {} if ok else {(i + 1, 0): C_BAD for i in range(k)}
    out.draw(base, font_size=40, fills=fills, text_cols=tc)
    src.outline(base, src.col_box(2), AMBER, a=0.5 + 0.5 * abs(math.sin(t * 6)), width=6)   # "copied" range
    d = ImageDraw.Draw(base)
    for sx, s in [(src.x + src.width() / 2, "Data"), (out.x + out.width() / 2, "Report")]:
        d.text((sx, SY - 40), s, font=F("Bold", 34), fill=MUTED, anchor="mm")
    ya = SY + src.hdr_h + src.row_h * 2.5
    arrow(d, src.x + src.width() + 8, ya, out.x - 8, ya, AMBER, width=8, head=22, a=ease(seg(t, t_fill - 0.3, t_fill)))
    if t >= t_fill + 0.35:
        r = back(seg(t, t_fill + 0.35, t_fill + 0.6)) * 40
        (check_icon if ok else cross_icon)(d, out.x + out.width() - 6, SY + out.height() + 10, r)
    return src, out

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "CTRL+V", RED, "It pastes the formula", y=280)
    demo(base, t, BAD, 1.0, False)
    keycaps(base, t, 0.45, ["Ctrl", "+", "V"], 1330, size=46, a=1 - ease(seg(t, 1.6, 1.8)))
    formula_bar(base, 150, 1290, 780, "=A2*B2", a=ease(seg(t, 1.8, 2.0)), size=50,
                colors=[("A2", (200, 40, 50)), ("B2", (200, 40, 50))])
    pop_text(base, "refs fall off the sheet", W / 2, 1470, F("Bold", 46), WHITE, t, 2.05, stroke=6)
    return shake(base, t, 1.0, 0.25, 12)

T_GS = 0.45 + 2 * 0.22 + 0.15
def sc_sheets(t, D):
    base = background()
    label_card(base, t, 0.0, "GOOGLE SHEETS", BLUE, "Paste values only", y=280, sub="Mac: Cmd + Shift + V")
    demo(base, t, VALS, T_GS, True)
    keycaps(base, t, 0.45, ["Ctrl", "+", "Shift", "+", "V"], 1360, size=48)
    return shake(base, t, T_GS + 0.35, 0.2, 10)

KEYS_XL = ["Ctrl", "+", "Alt", "+", "V", "then", "V", "then", "Enter"]
T_XL = 0.45 + 4 * 0.26 + 0.15
def sc_excel(t, D):
    base = background()
    label_card(base, t, 0.0, "EXCEL · WINDOWS", GREEN, "Paste Special > Values", y=280)
    demo(base, t, VALS, T_XL, True)
    keycaps(base, t, 0.45, KEYS_XL, 1360, size=40, gap=0.26)
    return shake(base, t, T_XL + 0.35, 0.2, 10)

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=290)
    info_rows(base, t, 0.3, [("Sheets: Ctrl+Shift+V", True), ("Sheets Mac: Cmd+Shift+V", True),
                             ("Excel: Ctrl+Alt+V, V, Enter", True)], y0=690, step=160, size=42)
    return base

def sc_outro(t, D):
    return loop_back(outro(t), sc_hook(0.0, 2.8), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.8),
    ("02_problem", sc_problem, 3.0),
    ("03_sheets", sc_sheets, 2.8),
    ("04_excel", sc_excel, 3.2),
    ("05_both", sc_both, 2.4),
    ("06_outro", sc_outro, 2.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.3, 0.6, 0.95))
        print(sum(D for *_, D in SCENES), "| totals", TOTALS, "| fonts", F1.size, F2.size, "| T_GS", T_GS, "T_XL", T_XL)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, FILL_T + 0.35, starts[1] + 1.0, starts[2] + T_GS, starts[3] + T_XL])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.2, 2.8).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
