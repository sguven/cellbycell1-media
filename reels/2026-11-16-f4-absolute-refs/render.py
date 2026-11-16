"""Reel: F4 - lock a cell reference with $ (Excel + Google Sheets).

Copying =B2*D2 down shifts D2 -> D3, D4... (empty) -> $0.00. =B2*$D$2 keeps the rate cell fixed.
While editing a formula, F4 cycles the reference under the cursor: D2 -> $D$2 -> D$2 -> $D2 -> D2.
Keys: Excel Windows F4 · Excel Mac Cmd+T · Google Sheets F4 (Mac: Fn+F4).

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> f4-absolute-refs.mp4 + cover.jpg
"""
import os, sys
from decimal import Decimal
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "f4-absolute-refs"
DATE = "2026-11-16"
ITEMS = [("Mug", "12"), ("Shirt", "25"), ("Lamp", "40"), ("Bag", "60")]   # rows 2..5
RATE = Decimal("0.08")                                                     # D2
N = len(ITEMS)

def money(v): return f"${v:.2f}"
# =B{r}*D{r} copied down: only row 2 has a rate next to it, D3:D5 are empty (= 0)
WRONG = [money(Decimal(p) * (RATE if i == 0 else Decimal(0))) for i, (_, p) in enumerate(ITEMS)]
# =B{r}*$D$2 copied down
RIGHT = [money(Decimal(p) * RATE) for _, p in ITEMS]

C_B = (40, 110, 220)     # B ref (blue)
C_D = (200, 120, 0)      # locked rate ref (amber)
C_BAD = (210, 50, 55)
BLUE_T = (214, 232, 255)
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)
RED_T = (255, 214, 214)
CW = [210, 180, 190, 170]
ROW_H = 84
FS = 40

def grid(y, tax):
    data = [["Item", "Price", "Tax", "Rate"]]
    for i, (a, p) in enumerate(ITEMS):
        data.append([a, f"${p}", tax[i] if tax else "", "8%" if i == 0 else ""])
    s = Sheet(0, y, CW, data, row_h=ROW_H)
    s.x = (W - s.width()) // 2
    return s

def bar(base, text, y, colors=None, t=None, t0=0.0, w=860, a=1.0, size=56):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, colors=colors, size=size, a=a)

# ---------- scenes ----------
HOOK_FONT = fit_font("Bold", "ALL $0.00?", 860, 190)

def sc_hook(t, D):
    base = background()
    pop_text(base, "ALL $0.00?", W / 2, 400, HOOK_FONT, AMBER, t, -0.15, stroke=10)
    fixed = t >= 1.15
    s = grid(600, RIGHT if fixed else WRONG)
    f, tc = {}, {}
    for r in range(1, N + 1):
        if fixed:
            if t >= 1.15 + (r - 1) * 0.08: f[(r, 2)] = GREEN_T
            else: f[(r, 2)] = RED_T
        elif r > 1: f[(r, 2)] = RED_T; tc[(r, 2)] = C_BAD
    s.draw(base, fills=f, text_cols=tc, font_size=FS)
    s.outline(base, s.cell_box(1, 3), AMBER, a=1.0 if fixed else 0.0, width=7)
    d = ImageDraw.Draw(base)
    bx = s.x + s.width(); by = s.y + s.hdr_h + 3 * ROW_H
    if not fixed:
        r = back(seg(t, 0.1, 0.35)) * 44
        if r > 2: cross_icon(d, bx, by, r)
    else:
        r = back(seg(t, 1.25, 1.5)) * 46
        if r > 2: check_icon(d, bx, by, r)
    keycaps(base, t, 0.95, ["F4"], 1290, size=72)
    fr = punch(base, t, 0.0, 0.08, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, 1.15, 0.2, 10)

def sc_why(t, D):
    base = background()
    label_card(base, t, 0.0, "WHY?", RED, "You copied it down", y=290)
    moved = t >= 1.0
    s = grid(780, WRONG if moved else [WRONG[0], "", "", ""])
    row = 1
    if moved: row = 1 + min(N - 1, 1 + int((t - 1.0) / 0.35))
    txt = f"=B{row + 1}*D{row + 1}"
    f, tc = {(row, 1): BLUE_T}, {}
    if moved:
        for r in range(2, row + 1): tc[(r, 2)] = C_BAD; f[(r, 2)] = RED_T
    s.draw(base, fills=f, text_cols=tc, font_size=FS)
    s.outline(base, s.cell_box(row, 2), (30, 120, 70), width=6)
    bad = row > 1
    s.outline(base, s.cell_box(row, 3), RED if bad else C_D, width=7, a=ease(seg(t, 0.3, 0.55)))
    bar(base, txt, 560, colors=[(f"B{row + 1}", C_B), (f"D{row + 1}", C_BAD if bad else C_D)],
        a=ease(seg(t, 0.15, 0.4)))
    if bad:
        b = s.cell_box(row, 3)
        pill(ImageDraw.Draw(base), (b[0] + b[2]) / 2, b[1] + ROW_H / 2, "empty", RED, size=28)
    return base

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Cursor on D2, hit F4", y=290)
    pressed = t >= 1.0
    txt = "=B2*$D$2" if pressed else "=B2*D2"
    bar(base, txt, 620, colors=[("B2", C_B), ("$D$2" if pressed else "D2", C_D)], a=ease(seg(t, 0.1, 0.35)))
    if pressed:
        p = seg(t, 1.0, 1.4)
        if p < 1:   # flash ring around the new $ signs
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            fm = F("Mono", 56); x0 = (W - 860) // 2 + 118 + fm.getlength("=B2*")
            g = 16 + 30 * p
            d.rounded_rectangle([x0 - g, 672 - 40 - g, x0 + fm.getlength("$D$2") + g, 672 + 40 + g], 20,
                                outline=rgba(AMBER, 1 - p), width=8)
            base.alpha_composite(lay)
    keycaps(base, t, 1.0, ["F4"], 980, size=90)
    fr = shake(base, t, 1.0, 0.22, 12)
    return fr

def sc_result(t, D):
    base = background()
    row = 1 + min(N - 1, int(seg(t, 0.35, 1.45) * N))
    bar(base, f"=B{row + 1}*$D$2", 340, colors=[(f"B{row + 1}", C_B), ("$D$2", C_D)])
    shown = [RIGHT[i] if i < row else "" for i in range(N)]
    s = grid(560, shown)
    f = {(r, 2): GREEN_T for r in range(1, row + 1)}
    f[(row, 1)] = BLUE_T
    s.draw(base, fills=f, font_size=FS)
    s.outline(base, s.cell_box(row, 2), (30, 120, 70), width=6)
    s.outline(base, s.cell_box(1, 3), AMBER, width=8)
    result_chip(base, W / 2, 1300, "D2 stays locked", True, t, 1.6)
    return base

MODES = [("$D$2", "locks column + row"), ("D$2", "locks the row only"),
         ("$D2", "locks the column only"), ("D2", "locks nothing")]

def sc_cycle(t, D):
    base = background()
    label_card(base, t, 0.0, "KEEP PRESSING F4", AMBER, "4 modes, 1 key", y=290)
    k = clamp(int((t - 0.35) / 0.62), 0, 3)
    t0 = 0.35 + k * 0.62
    if t >= 0.35:
        tok, s = MODES[k]
        pop_text(base, tok, W / 2, 800, F("Mono", 170), AMBER, t, t0, stroke=0, dur=0.25)
        pop_text(base, s, W / 2, 1010, F("Bold", 60), WHITE, t, t0 + 0.05, stroke=0, dur=0.25)
        d = ImageDraw.Draw(base)
        for i in range(4):
            cx = W / 2 + (i - 1.5) * 60
            d.ellipse([cx - 13, 1150 - 13, cx + 13, 1150 + 13], fill=AMBER if i <= k else NAVY3)
    return base

def sc_both(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Excel & Google Sheets", y=300)
    info_rows(base, t, 0.35, [("Excel (Windows):  F4", True), ("Excel (Mac):  Cmd + T", True),
                              ("Sheets:  F4  (Mac: Fn + F4)", True)], y0=660, step=160, size=44)
    return base

def sc_outro(t, D):
    return loop_back(outro(t), sc_hook(0.0, 2.7), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.7),
    ("02_why", sc_why, 2.8),
    ("03_fix", sc_fix, 2.8),
    ("04_result", sc_result, 2.8),
    ("05_cycle", sc_cycle, 3.0),
    ("06_both", sc_both, 2.6),
    ("07_outro", sc_outro, 2.6),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "|", WRONG, "|", RIGHT, "| hook font", HOOK_FONT.size)
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 1.15, starts[2] + 1.0, starts[3] + 1.6])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.7).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
