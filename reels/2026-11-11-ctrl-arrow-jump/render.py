"""Reel: Jump to the end of your data in 1 keystroke (Excel + Google Sheets).

Ctrl+Arrow   = move to the edge of the current data region (Excel Windows; same keys in Google Sheets).
Ctrl+Shift+Arrow = extend the selection to the last nonblank cell in that column/row.
Mac: Cmd+Arrow / Cmd+Shift+Arrow. Blank cells are "stop signs": each press jumps to the next edge.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> ctrl-arrow-jump.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "ctrl-arrow-jump"
DATE = "2026-11-11"
DOWN = "↓"
K_JUMP = ["Ctrl", "+", DOWN]
K_SEL = ["Ctrl", "+", "Shift", "+", DOWN]

# ---- the demo data: an order log in rows 2..5000 (header in row 1); every value on screen comes from here
LAST = 5000
def order_id(r): return 1000 + (r - 1)                          # row 2 -> 1001, row 5000 -> 5999
def amount_cents(r): return 1200 + (r * 7919) % 18800           # $12.00 .. $199.99, deterministic
def money(c): return f"${c // 100:,}.{c % 100:02d}"
def row(r): return [str(order_id(r)), money(amount_cents(r))]
N_SEL = LAST - 2 + 1                                            # cells in B2:B5000
SUM_SEL = sum(amount_cents(r) for r in range(2, LAST + 1))

# ---- the gap demo: rows 1..8, row 5 blank; jump targets computed with the spreadsheet rule
GAP_ROWS = {1: ["Order ID", "Amount"], 2: row(2), 3: row(3), 4: row(4), 5: ["", ""], 6: row(5), 7: row(6), 8: row(7)}
def ctrl_down(filled, r, last=1048576):
    """Edge rule for Ctrl+Down: inside a block -> last filled cell of the block; else -> next filled cell (or sheet end)."""
    if r in filled and r + 1 in filled:
        while r + 1 in filled: r += 1
        return r
    r += 1
    while r not in filled and r < last: r += 1
    return r
GAP_FILLED = {r for r, v in GAP_ROWS.items() if v[0]}
GAP_STOPS = [2]
for _ in range(3): GAP_STOPS.append(ctrl_down(GAP_FILLED, GAP_STOPS[-1]))
assert GAP_STOPS == [2, 4, 6, 8], GAP_STOPS
assert ctrl_down(set(range(1, LAST + 1)), 2) == LAST

FS = 42
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)
BLUE_T = (214, 230, 255)
DARK_GREEN = (20, 140, 90)
CUR_COL = (230, 140, 0)

def sheet(data, cw, y, row_h=84, labels=None):
    s = Sheet(0, y, cw, data, row_h=row_h, row_labels=labels)
    s.x = (W - s.width()) // 2
    return s

def cursor(base, s, box, landed):
    s.outline(base, box, DARK_GREEN if landed else CUR_COL, width=9)

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "STOP", W / 2, 360, F("Bold", 200), AMBER, t, -0.15, stroke=10)
    pop_text(base, "scrolling", W / 2, 540, F("Bold", 110), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.25:
        pill(d, W / 2, 670, f"ROW {LAST:,} IN 1 KEYSTROKE", RED, size=40, a=ease(seg(t, 0.25, 0.5)))
    for y, ok, t0 in ((850, False, 0.35), (1080, True, 0.7)):
        p = ease(seg(t, t0, t0 + 0.3))
        if p <= 0: continue
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        yy = y + (1 - p) * 40
        ld.rounded_rectangle([70, yy - 100, W - 70, yy + 100], 40, fill=rgba(NAVY2, p))
        ld.rounded_rectangle([70, yy - 100, 84, yy + 100], 6, fill=rgba(GREEN if ok else RED, p))
        (check_icon if ok else cross_icon)(ld, 150, yy, 44, a=p)
        if not ok:
            ld.text((220, yy - 30), "Scroll... scroll...", font=F("Bold", 56), fill=rgba(WHITE, p), anchor="lm")
            ld.text((220, yy + 45), "hunting for the last row", font=F("Medium", 40), fill=rgba(MUTED, p), anchor="lm")
            q = ease(seg(t, t0 + 0.3, t0 + 0.55))
            if q > 0: ld.line([(210, yy - 26), (210 + 500 * q, yy - 26)], fill=rgba(RED, p), width=6)
        base.alpha_composite(lay)
        if ok:
            keycaps(base, t, t0 + 0.1, K_JUMP, yy - 32, size=44, gap=0.18, cx=350, a=p)
            ImageDraw.Draw(base).text((220, yy + 52), f"lands on row {LAST:,} instantly", font=F("Medium", 40),
                                      fill=rgba(MUTED, p), anchor="lm")
    q = ease(seg(t, 0.85, 1.15))
    if q > 0:
        landed = t > HOOK_PRESS + 0.05
        s = sheet([["Order ID", "Amount"], row(2), row(LAST)], [330, 300], y=1240 + (1 - q) * 40,
                  labels=["1", "2", str(LAST)])
        s.draw(base, a=q, font_size=FS, fills={(2 if landed else 1, 0): GREEN_T if landed else AMBER_T})
        p = ease(seg(t, HOOK_PRESS, HOOK_PRESS + 0.18))
        cursor(base, s, lerp_box(s.cell_box(1, 0), s.cell_box(2, 0), p), landed)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)
HOOK_PRESS = 0.7 + 0.1 + 2 * 0.18     # last keycap of the "good" card

SCROLL_END = 1904
def scroll_top(t):
    p = seg(t, 0.5, 2.6)
    return 2 + int((SCROLL_END - 2) * p ** 2.2)

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "THE SLOW WAY", RED, "Scroll... and scroll...", sub=f"{LAST:,} rows of orders")
    top = scroll_top(t)
    rows = [top + i for i in range(7)]
    s = sheet([["Order ID", "Amount"]] + [row(r) for r in rows], [330, 300], y=600,
              labels=["1"] + [f"{r:,}".replace(",", "") for r in rows], row_h=84)
    s.draw(base, font_size=FS)
    # scrollbar crawling down
    d = ImageDraw.Draw(base)
    x0 = s.x + s.width() + 30; y0, y1 = s.y, s.y + s.height()
    d.rounded_rectangle([x0, y0, x0 + 18, y1], 9, fill=NAVY2)
    th = 70; ty = y0 + (y1 - y0 - th) * (top - 2) / (LAST - 2)
    d.rounded_rectangle([x0, ty, x0 + 18, ty + th], 9, fill=AMBER)
    if t > 2.6:
        pill(d, W / 2, 1405, f"Row {top:,}... still not the end", NAVY2, size=40, a=ease(seg(t, 2.6, 2.85)))
    result_chip(base, W / 2, 1505, "Slow and easy to overshoot", False, t, 2.9)
    return base

JUMP_LABELS = ["1", "2", "3", "4", "⋮", str(LAST - 1), str(LAST)]
JUMP_DATA = [["Order ID", "Amount"], row(2), row(3), row(4), ["", ""], row(LAST - 1), row(LAST)]

def sc_jump(t, D):
    base = background()
    label_card(base, t, 0.0, "STEP 1 · JUMP", GREEN, "Ctrl + Down Arrow", sub="Lands on the last filled cell")
    t_press = keycaps(base, t, 0.8, K_JUMP, 1330, size=48, gap=0.22)
    landed = t > t_press + 0.15
    s = sheet(JUMP_DATA, [330, 300], y=690, row_h=72, labels=JUMP_LABELS)
    s.draw(base, font_size=40, fills={(6 if landed else 1, 0): GREEN_T if landed else AMBER_T})
    p = ease(seg(t, t_press, t_press + 0.2))
    cursor(base, s, lerp_box(s.cell_box(1, 0), s.cell_box(6, 0), p), landed)
    name_box(base, W / 2, 615, f"A{LAST}" if landed else "A2", flash=1 - seg(t, t_press + 0.15, t_press + 0.6) if landed else 0)
    result_chip(base, W / 2, 1480, f"A{LAST}: order #{order_id(LAST)}", True, t, t_press + 0.45)
    return base
def jump_press(): return 0.8 + 2 * 0.22

def sc_select(t, D):
    base = background()
    label_card(base, t, 0.0, "STEP 2 · SELECT", GREEN, "Add Shift", sub="Selects everything down to the end")
    t_press = keycaps(base, t, 0.8, K_SEL, 1290, size=44, gap=0.2)
    p = ease(seg(t, t_press, t_press + 0.3))
    s = sheet(JUMP_DATA, [330, 300], y=640, row_h=72, labels=JUMP_LABELS)
    fills = {(1, 1): AMBER_T}
    if p > 0: fills = {(r, 1): BLUE_T for r in range(1, 7) if r <= 1 + p * 5 + 0.01}
    s.draw(base, font_size=40, fills=fills)
    b0 = s.cell_box(1, 1); b1 = s.cell_box(6, 1)
    s.outline(base, [b0[0], b0[1], b0[2], b0[3] + (b1[3] - b0[3]) * p], BLUE if p > 0 else CUR_COL, width=9)
    if t > t_press + 0.35:
        d = ImageDraw.Draw(base)
        pill(d, W / 2, 1405, f"Count: {N_SEL:,}    Sum: {money(SUM_SEL)}", NAVY2, size=36,
             a=ease(seg(t, t_press + 0.35, t_press + 0.6)))
    result_chip(base, W / 2, 1505, f"B2:B{LAST} selected", True, t, t_press + 0.7)
    return base
def select_press(): return 0.8 + 2 * 0.2

GAP_TIMES = [1.3, 2.5, 3.7]       # the 3 presses
def sc_gap(t, D):
    base = background()
    label_card(base, t, 0.0, "WATCH OUT", AMBER, "Blank cells stop it", sub="Press again to keep going")
    keycaps(base, t, GAP_TIMES[0] - 2 * 0.2, K_JUMP, 1330, size=44, gap=0.2)
    k = sum(1 for g in GAP_TIMES if t >= g)
    data = [GAP_ROWS[r] for r in range(1, 9)]
    s = sheet(data, [330, 300], y=590, row_h=72)
    cur = GAP_STOPS[k]; prev = GAP_STOPS[max(0, k - 1)]
    p = ease(seg(t, GAP_TIMES[k - 1], GAP_TIMES[k - 1] + 0.2)) if k else 1.0
    landed = k == 3 and p >= 1
    fills = {(4, 0): (255, 222, 223), (4, 1): (255, 222, 223)}
    fills[(cur - 1, 0)] = GREEN_T if landed else AMBER_T
    s.draw(base, font_size=40, fills=fills)
    cursor(base, s, lerp_box(s.cell_box(prev - 1, 0), s.cell_box(cur - 1, 0), p), landed)
    d = ImageDraw.Draw(base)
    if t > 0.5:
        bx = s.cell_box(4, 1)
        d.text((bx[2] + 24, (bx[1] + bx[3]) / 2), "blank", font=F("Bold", 34), fill=rgba(RED, ease(seg(t, 0.5, 0.8))), anchor="lm")
    if k:
        pill(d, W / 2, 1450, f"PRESS {k}  ·  A{cur}", AMBER if landed else NAVY2, fg=NAVY if landed else WHITE, size=40)
    return base

def sc_works(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=380)
    info_rows(base, t, 0.4, [
        ("Ctrl + Arrow: jump to the edge", True),
        ("Ctrl + Shift + Arrow: select it", True),
        ("Mac: Cmd instead of Ctrl", None),
    ], y0=760, step=170, size=44)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_problem", sc_problem, 4.2),
    ("03_jump", sc_jump, round(jump_press() + 3.0, 2)),
    ("04_select", sc_select, round(select_press() + 3.4, 2)),
    ("05_gap", sc_gap, 5.4),
    ("06_works", sc_works, 4.0),
    ("07_outro", sc_outro, 3.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.4, 0.65, 0.95))
        print([(n, D) for n, _, D in SCENES], sum(D for *_, D in SCENES), N_SEL, money(SUM_SEL), row(LAST), GAP_STOPS)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, HOOK_PRESS, starts[2] + jump_press(), starts[3] + select_press(),
                                            starts[4] + GAP_TIMES[-1]])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
