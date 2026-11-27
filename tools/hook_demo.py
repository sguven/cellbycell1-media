"""One worked example of each opening format in lib/hooks.py, on real calendar topics.

python3 tools/hook_demo.py stills <outdir>   -> contact sheet per format (t = 0, 0.3, 0.8, 1.5, 2.2 s)
python3 tools/hook_demo.py mp4 <out.mp4>     -> silent preview, the three openings back to back

Copy the matching sc_* function into the day's render.py as sc_hook and adapt the data/texts to the topic.
Every value on screen is computed from the table (accuracy rule).
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from engine import *
from hooks import *
from PIL import Image, ImageDraw

D_HOOK = 2.4
GREEN_T, RED_T, AMBER_T = (214, 242, 228), (253, 222, 223), (255, 240, 206)

# ---------- 1. quiz_open: percent-change ----------
OLD, NEW = 80, 100
RIGHT = f"{(NEW - OLD) / OLD:.0%}"            # 25%
WRONG = f"{(NEW - OLD) / NEW:.0%}"            # 20% (the common mistake: dividing by the new value)
assert (RIGHT, WRONG) == ("25%", "20%")
Q_DATA = [["Before", "Now", "Change"], [f"${OLD}", f"${NEW}", "?"]]
T_REV = 1.8

def sc_quiz(t, D):
    base = screen_bg()
    s = big_sheet([r[:] for r in Q_DATA], [10, 10, 10], y=540, row_h=210)
    rv = t >= T_REV
    if rv: s.data[1][2] = RIGHT
    s.draw(base, font_size=64, fills={(1, 2): GREEN_T if rv else AMBER_T},
           text_cols={(1, 2): GREEN if rv else (200, 130, 0)})
    s.outline(base, s.cell_box(1, 2), GREEN if rv else AMBER, width=8)
    sticker(base, "What's the % change?", 390, t, -0.2, size=78)
    quiz_cards(base, t, WRONG, RIGHT, "b", y=1090, t_in=0.0, t_reveal=T_REV, h=320, size=120)
    fr = camera(base, t, 0.0, T_REV, 1.0, 1.06, focus=(0.5, 0.52))
    return shake_bg(fr, t, T_REV, 0.3, 16)

# ---------- 2. cold_open: proper-case-names ----------
NAMES = ["MARIA LOPEZ", "DAVID CHEN", "SARA KHAN", "TOM BAKER", "NINA PATEL"]
FIXED = [n.title() for n in NAMES]            # what =PROPER() returns for these names

def sc_cold(t, D):
    base = screen_bg()
    data = [["Name", "Clean"]] + [[n, ""] for n in NAMES]
    fills, cols = {}, {}
    for i in range(len(NAMES)):
        t0 = 0.10 + i * 0.16                  # the fix is already running at frame 3
        if t >= t0:
            data[i + 1][1] = FIXED[i]; fills[(i + 1, 1)] = GREEN_T; cols[(i + 1, 1)] = (16, 120, 74)
        fills[(i + 1, 0)] = RED_T
    s = big_sheet(data, [10, 10], y=400, row_h=138)
    s.draw(base, font_size=50, fills=fills, text_cols=cols)
    k = min(len(NAMES), int(max(0, t - 0.10) / 0.16) + 1)
    if t >= 0.10:
        b0, b1 = s.cell_box(1, 1), s.cell_box(k, 1)
        s.outline(base, [b0[0], b0[1], b1[2], b1[3]], GREEN, width=8)
    sticker(base, ["ALL CAPS names?", "Fixed in 1 second"], 1440, t, 0.35, size=66)
    fr = camera(base, t, 0.0, 1.1, 1.10, 1.0, focus=(0.5, 0.42))
    return shake_bg(fr, t, 0.10 + len(NAMES) * 0.16, 0.25, 12)

# ---------- 3. chat_open: if-and-or ----------
ROWS = [("Ava", 82, "Yes"), ("Ben", 91, "No"), ("Cara", 64, "Yes"), ("Dev", 75, "Yes")]
RES = ["Pass" if sc >= 70 and att == "Yes" else "Fail" for _, sc, att in ROWS]   # =IF(AND(B2>=70,C2="Yes"),"Pass","Fail")
assert RES == ["Pass", "Fail", "Fail", "Pass"]

def sc_chat(t, D):
    base = screen_bg()
    yb = chat_bubble(base, "Who passed? I need it in 5 minutes.", 290, t, -0.3, who="Manager")
    typing_dots(base, yb + 30, t, 0.0, 0.75)
    chat_bubble(base, "Give me 5 seconds.", yb + 30, t, 0.75, side="right")
    data = [["Name", "Score", "Came?", "Result"]] + [[n, str(sc), att, ""] for n, sc, att in ROWS]
    fills, cols = {}, {}
    for i, r in enumerate(RES):
        t0 = 1.15 + i * 0.14
        if t >= t0:
            data[i + 1][3] = r; fills[(i + 1, 3)] = GREEN_T if r == "Pass" else RED_T
            cols[(i + 1, 3)] = (16, 120, 74) if r == "Pass" else (190, 50, 56)
    p = ease(seg(t, 0.0, 0.5))
    s = big_sheet(data, [9, 8, 8, 9], y=830 + int((1 - p) * 90), row_h=128)
    s.draw(base, font_size=46, fills=fills, text_cols=cols)
    if t >= 1.15: s.outline(base, s.col_box(3), AMBER, width=8)
    fr = camera(base, t, 0.0, 1.2, 1.08, 1.0, focus=(0.5, 0.35))
    return shake_bg(fr, t, 1.15, 0.25, 12)

DEMOS = [("quiz_open", sc_quiz), ("cold_open", sc_cold), ("chat_open", sc_chat)]

if __name__ == "__main__":
    mode, out = sys.argv[1], sys.argv[2]
    if mode == "stills":
        os.makedirs(out, exist_ok=True)
        ts = (0.0, 0.3, 0.8, 1.5, 2.2)
        for name, fn in DEMOS:
            sheet = Image.new("RGB", (540 * len(ts), 960))
            for i, t in enumerate(ts):
                sheet.paste(fn(t, D_HOOK).convert("RGB").resize((540, 960), Image.LANCZOS), (540 * i, 0))
            sheet.save(os.path.join(out, f"{name}.jpg"), quality=88)
            fn(0.0, D_HOOK).convert("RGB").save(os.path.join(out, f"{name}_frame0.jpg"), quality=90)
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for name, fn in DEMOS:
            for k in range(int((D_HOOK + 0.6) * FPS)):
                pr.stdin.write(fn(min(k / FPS, D_HOOK), D_HOOK).convert("RGB").tobytes())
        pr.stdin.close(); pr.wait()
