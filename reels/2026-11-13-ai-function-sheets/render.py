"""Reel: =AI() - an AI formula inside a Google Sheets cell (extra post, 2026-11-13).

Checked 2026-11-13 against Google Docs Editors Help "Use the AI function in Google Sheets" (answer 15877199):
  syntax AI("prompt", [optional range]); =Gemini() is an alias; needs an eligible Google Workspace or Google AI plan;
  on a computer: type the formula, select the cell, click "Generate and Insert" ("Refresh and Insert" to regenerate);
  text answers only; nesting (=IF(AI(...))) is not supported; no access to the rest of the file.
Excel: Microsoft Support "COPILOT function" says the function is no longer available from September 14, 2026
  (old cells return #NAME? on recalculation) and points to the Copilot pane instead.
The labels shown in column B are EXAMPLE output for unambiguous reviews (AI output can vary) and are flagged on screen.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> ai-function-sheets.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "ai-function-sheets"
DATE = "2026-11-13"
ROWS = [("Love it, works great!", "Positive"),
        ("Broke after two days", "Negative"),
        ("Fast shipping, thanks", "Positive"),
        ("Too loud, sent it back", "Negative"),
        ("It's okay for the price", "Neutral"),
        ("Best purchase this year", "Positive")]
N = len(ROWS)

F_AI = '=AI("Positive, negative or neutral?", A2)'
MORE = [("SUMMARIZE", '=AI("Summarize in 5 words", A2)'),
        ("REPLY", '=AI("Write a polite reply", A2)'),
        ("CATEGORIZE", '=AI("Price, quality or shipping?", A2)')]
C_SRC = (200, 120, 0)
C_FN = (20, 140, 90)

CW = [540, 290]
ROW_H = 78
FS = 36
SHEET_Y = 660
BAR_Y = 505
BAR_W = 980
CHIP_Y = 1390
AMBER_T = (255, 236, 196)
GREEN_T = (210, 244, 226)
RED_T = (255, 222, 222)
TINT = {"Positive": GREEN_T, "Negative": RED_T, "Neutral": AMBER_T}

def sheet(n_done=0, rows=ROWS, y=SHEET_Y, row_h=ROW_H):
    data = [["Review", "Mood"]] + [[r, m if i < n_done else ""] for i, (r, m) in enumerate(rows)]
    s = Sheet(0, y, CW, data, row_h=row_h)
    s.x = (W - s.width()) // 2
    return s

def mood_fills(n_done, rows=ROWS):
    return {(i + 1, 1): TINT[rows[i][1]] for i in range(n_done)}

def bar(base, text, t=None, t0=0.0, colors=None, y=BAR_Y, w=BAR_W, a=1.0):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, colors=colors, size=fit_formula_size(text, w), a=a)

def button(base, cx, cy, s, t, t0, t_click):
    """Drawn 'Generate and Insert' button that pops in and flashes when clicked."""
    p = ease(seg(t, t0, t0 + 0.3))
    if p <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = F("Bold", 44)
    w = f.getlength(s) + 110; h = 104
    k = seg(t, t_click, t_click + 0.35)
    pressed = 0 < k < 1
    sc = 1 - 0.05 * (1 - abs(2 * k - 1)) if pressed else 1
    w2, h2 = w * sc, h * sc
    cy2 = cy + (1 - p) * 30
    d.rounded_rectangle([cx - w2 / 2, cy2 - h2 / 2, cx + w2 / 2, cy2 + h2 / 2], h2 / 2,
                        fill=rgba(WHITE if pressed else AMBER, p))
    d.text((cx, cy2), s, font=f, fill=rgba(NAVY, p), anchor="mm")
    if pressed:
        r = 70 + 90 * k
        d.ellipse([cx - r * 2.6, cy2 - r, cx + r * 2.6, cy2 + r], outline=rgba(AMBER, 1 - k), width=8)
    base.alpha_composite(lay)

# ---------- scenes ----------
def sc_hook(t, D):
    base = background()
    pop_text(base, "=AI()", W / 2, 410, F("Bold", 230), AMBER, t, -0.15, stroke=10)
    pop_text(base, "AI INSIDE A CELL", W / 2, 610, F("Bold", 100), WHITE, t, -0.05, stroke=8)
    d = ImageDraw.Draw(base)
    if t > 0.3:
        pill(d, W / 2, 755, "GOOGLE SHEETS · 1 FORMULA", AMBER, fg=NAVY, size=40, a=ease(seg(t, 0.3, 0.55)))
    rows = ROWS[:4]
    n = sum(1 for k in range(len(rows)) if t > 0.55 + 0.2 * k)
    s = sheet(n, rows=rows, y=880)
    a = ease(seg(t, 0.25, 0.5))
    if a > 0:
        s.draw(base, a=a, fills=mood_fills(n, rows), font_size=FS)
    result_chip(base, W / 2, 1390, "It reads your text", True, t, 1.3)
    f = punch(base, t, 0.0, 0.08, 0.6)
    return shake(f, t, 0.02, 0.3, 16)

def sc_chore(t, D):
    base = background()
    label_card(base, t, 0.0, "THE CHORE", RED, "Tag every review by hand?", y=290)
    s = sheet(0)
    s.draw(base, font_size=FS)
    if t > 0.9:
        b0 = s.cell_box(1, 1); b1 = s.cell_box(N, 1)
        s.outline(base, [b0[0], b0[1], b1[2], b1[3]], RED, a=ease(seg(t, 0.9, 1.2)))
    result_chip(base, W / 2, CHIP_Y, "Slow, boring, error-prone", False, t, 1.6)
    return base

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "THE FIX", GREEN, "Ask AI in a formula", y=290)
    done = 1 if t > 3.55 else 0
    s = sheet(done)
    s.draw(base, fills=mood_fills(done), font_size=FS)
    s.outline(base, s.cell_box(1, 0), AMBER, a=ease(seg(t, 1.7, 1.95)))
    s.outline(base, s.cell_box(1, 1), GREEN, a=ease(seg(t, 0.3, 0.6)))
    bar(base, F_AI, t, 0.4, colors=[("AI", C_FN), ("A2", C_SRC)])
    button(base, W / 2, CHIP_Y - 60, "Generate and Insert", t, 2.2, 3.1)
    pop_text(base, "type it, select the cell, click the button", W / 2, CHIP_Y + 50, F("Medium", 40), MUTED, t, 2.5, stroke=0)
    result_chip(base, W / 2, CHIP_Y + 170, "Gemini reads A2", True, t, 3.7)
    return base

def sc_fill(t, D):
    base = background()
    label_card(base, t, 0.0, "FILL IT DOWN", AMBER, "Every row, labeled", y=290)
    n = 1 + sum(1 for k in range(N - 1) if t > 0.6 + k * 0.25)
    s = sheet(n)
    s.draw(base, fills=mood_fills(n), font_size=FS)
    if n < N: s.outline(base, s.cell_box(n, 1), GREEN, a=1)
    result_chip(base, W / 2, CHIP_Y, f"{N} reviews tagged", True, t, 2.2)
    pop_text(base, "Example output: AI answers can vary, spot-check them", W / 2, CHIP_Y + 115, F("Medium", 36), MUTED, t, 2.8, stroke=0)
    return base

def sc_more(t, D):
    base = background()
    label_card(base, t, 0.0, "SAME TRICK", AMBER, "Just change the prompt", y=290)
    for i, (tag, f) in enumerate(MORE):
        t0 = 0.5 + i * 1.15
        a = ease(seg(t, t0, t0 + 0.3))
        if a <= 0: continue
        y = 640 + i * 250
        pill(ImageDraw.Draw(base), W / 2, y, tag, NAVY2, fg=AMBER, size=36, a=a)
        bar(base, f, t, t0 + 0.15, colors=[("AI", C_FN), ("A2", C_SRC)], y=y + 55, a=a)
    return base

def sc_limits(t, D):
    base = background()
    label_card(base, t, 0.0, "HEADS UP", RED, "Know the limits", y=330)
    info_rows(base, t, 0.4, [("Answers are text only", None),
                             ("Data changed? Click Refresh", None),
                             ("Can't nest it inside IF()", False),
                             ("Always check what AI wrote", None)], y0=660, step=160, size=44)
    return base

def sc_where(t, D):
    base = background()
    label_card(base, t, 0.0, "WORKS IN", AMBER, "Google Sheets only", y=330)
    info_rows(base, t, 0.4, [("Google Sheets, on a computer", True),
                             ("Needs a Workspace or Google AI plan", None),
                             ("Excel: =COPILOT() retired Sept 2026", False),
                             ("Excel: ask the Copilot pane instead", None)], y0=660, step=160, size=37)
    return base

def sc_outro(t, D): return outro(t)

SCENES = [
    ("01_hook", sc_hook, 3.2),
    ("02_chore", sc_chore, 3.6),
    ("03_fix", sc_fix, 5.8),
    ("04_fill", sc_fill, 4.8),
    ("05_more", sc_more, 5.2),
    ("06_limits", sc_limits, 4.4),
    ("07_where", sc_where, 4.6),
    ("08_outro", sc_outro, 3.4),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.15, 0.5, 0.95))
        print(sum(D for *_, D in SCENES))
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, 1.3, starts[2] + 3.55, starts[3] + 2.2])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.4, 3.2).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
