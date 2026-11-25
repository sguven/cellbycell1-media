"""Reel: Pivot table in 1 formula? GROUPBY (Excel for Microsoft 365) + QUERY alternative for Google Sheets.

Sources checked 2026-11-25:
  Microsoft Support "GROUPBY function" (Applies To: Excel for Microsoft 365):
    GROUPBY(row_fields,values,function,[field_headers],[total_depth],[sort_order],[filter_array],[field_relationship])
    function = eta-reduced lambda such as SUM; total_depth 0 = no totals; sort_order -2 = descending by column 2
    (Microsoft's own example: =GROUPBY(C2:C76,D2:D76,SUM,,,-2)). field_headers omitted = automatic; B2 is a number,
    so no header row is generated. The headers in D1:E1 are typed by hand; the formula sits in D2 and spills to D2:E5.
  Google Docs Editors Help "QUERY function": QUERY(data, query, [headers]); "select A, sum(B) group by A".
  GROUPBY is not in Google Sheets, so the Sheets scene shows QUERY instead (formula only, no result drawn).
All totals on screen are computed below from the table.

python3 render.py stills   -> preview frames in ./stills
python3 render.py          -> groupby-one-formula.mp4 + cover.jpg
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
from engine import *
from PIL import Image, ImageDraw
import music_upbeat, music_styles

SLUG = "groupby-one-formula"
DATE = "2026-11-25"

SALES = [("East", 450), ("West", 300), ("North", 520), ("East", 380),
         ("South", 210), ("West", 640), ("North", 150), ("East", 270)]          # A2:B9
TOT = {}
for r, v in SALES: TOT[r] = TOT.get(r, 0) + v
SUMMARY = sorted(TOT.items(), key=lambda kv: -kv[1])                            # sort_order -2 (descending)
assert SUMMARY == [("East", 1100), ("West", 940), ("North", 670), ("South", 210)]
EAST_ROWS = [i + 1 for i, (r, _) in enumerate(SALES) if r == "East"]           # data row indexes in the Sheet
EAST_SUM = "+".join(str(v) for r, v in SALES if r == "East")
assert EAST_SUM == "450+380+270" and TOT["East"] == 1100

F_FIX = "=GROUPBY(A2:A9,B2:B9,SUM,,0,-2)"
F_GS = '=QUERY(A1:B9,"select A, sum(B) group by A")'
C_A = (200, 120, 0)
C_B = (40, 110, 220)
TINT = {"East": (255, 236, 196), "West": (214, 232, 255), "North": (212, 244, 226), "South": (240, 224, 250)}
CW = [180, 140, 40, 180, 150]
ROW_H = 70
FS = 38

def grid(y, n_spill=0, row_h=ROW_H):
    data = [["Region", "Sales", "", "Region", "Total"]]
    for i, (r, v) in enumerate(SALES):
        data.append([r, str(v), ""] + ([SUMMARY[i][0], str(SUMMARY[i][1])] if i < min(n_spill, 4) else ["", ""]))
    s = Sheet(0, y, CW, data, row_h=row_h)
    s.x = (W - s.width()) // 2
    return s

def src_fills(rows=None):
    return {(i + 1, c): TINT[r] for i, (r, _) in enumerate(SALES) for c in (0, 1) if rows is None or i + 1 in rows}

def spill_fills(n):
    return {(i + 1, c): TINT[SUMMARY[i][0]] for i in range(min(n, 4)) for c in (3, 4)}

def spill_count(t, t0, gap=0.12):
    return 0 if t < t0 else min(4, 1 + int((t - t0) / gap))

def bar(base, text, y, colors=None, t=None, t0=0.0, w=960, cps=30):
    formula_bar(base, (W - w) // 2, y, w, text, t=t, t0=t0, cps=cps, colors=colors,
                size=fit_formula_size(text, w, max_size=50))

# ---------- scenes ----------
HOOK = ["PIVOT", "TABLE IN", "1 FORMULA?"]
HF = fit_font("Bold", max(HOOK, key=len), 990, 178)
T_SPILL = 0.35

def sc_hook(t, D):
    base = background()
    for i, ln in enumerate(HOOK):
        pop_text(base, ln, W / 2, 345 + i * 168, HF, AMBER, t, -0.5 + i * 0.04, stroke=10)
    n = spill_count(t, T_SPILL)
    s = grid(790, n, row_h=62)
    f = src_fills(); f.update(spill_fills(n))
    s.draw(base, fills=f, font_size=FS)
    a = ease(seg(t, T_SPILL, T_SPILL + 0.2))
    if a > 0: s.outline(base, [s.col_x(3), s.cell_box(1, 3)[1], s.col_x(4) + CW[4], s.cell_box(4, 4)[3]], GREEN, a=a, width=7)
    result_chip(base, W / 2, 1490, "4 totals, 1 formula", True, t, 0.85)
    fr = punch(base, t, 0.0, 0.045, 0.6)
    fr = shake(fr, t, 0.02, 0.3, 16)
    return shake(fr, t, 0.85, 0.2, 10)

def sc_problem(t, D):
    base = background()
    label_card(base, t, 0.0, "BY HAND", RED, "Add up every region?", y=290)
    s = grid(600)
    lit = [r for k, r in enumerate(EAST_ROWS) if t >= 0.35 + k * 0.25]
    s.draw(base, fills=src_fills(lit), font_size=FS)
    for k, r in enumerate(EAST_ROWS):
        a = ease(seg(t, 0.35 + k * 0.25, 0.5 + k * 0.25))
        if a > 0:
            b = s.cell_box(r, 0); s.outline(base, [b[0], b[1], s.cell_box(r, 1)[2], b[3]], RED, a=a, width=6)
    result_chip(base, W / 2, 1420, f"{EAST_SUM} ... x4", False, t, 1.25)
    return shake(base, t, 1.25, 0.2, 10)

T_TYPE = 0.2
T_FIX = T_TYPE + len(F_FIX) / 34 + 0.15

def sc_fix(t, D):
    base = background()
    label_card(base, t, 0.0, "EXCEL 365", GREEN, "One formula: GROUPBY", y=290)
    bar(base, F_FIX, 492, colors=[("A2:A9", C_A), ("B2:B9", C_B)], t=t, t0=T_TYPE, cps=34)
    n = spill_count(t, T_FIX, 0.1)
    s = grid(640, n)
    f = src_fills() if t >= T_FIX else {}
    f.update(spill_fills(n))
    s.draw(base, fills=f, font_size=FS)
    s.outline(base, s.col_box(0, 1, 8), C_A, a=ease(seg(t, 0.45, 0.65)) * (1 - seg(t, T_FIX, T_FIX + 0.2)), width=6)
    s.outline(base, s.col_box(1, 1, 8), C_B, a=ease(seg(t, 0.75, 0.95)) * (1 - seg(t, T_FIX, T_FIX + 0.2)), width=6)
    a = ease(seg(t, T_FIX, T_FIX + 0.2))
    if a > 0: s.outline(base, [s.col_x(3), s.cell_box(1, 3)[1], s.col_x(4) + CW[4], s.cell_box(4, 4)[3]], GREEN, a=a, width=7)
    result_chip(base, W / 2, 1440, "Sorted, biggest first", True, t, T_FIX + 0.35)
    return shake(base, t, T_FIX, 0.2, 12)

def sc_how(t, D):
    base = background()
    label_card(base, t, 0.0, "HOW IT WORKS", AMBER, "Group, add, sort", y=290)
    arg_rows(base, t, 0.3, [("A2:A9", C_A, "group by Region"),
                            ("B2:B9", C_B, "values to add"),
                            ("SUM", GREEN, "how to combine"),
                            ("0,-2", RED, "no total, biggest first")], y0=640, step=158, gap=0.35, size=42)
    return base

def sc_sheets(t, D):
    base = background()
    label_card(base, t, 0.0, "GOOGLE SHEETS", BLUE, "Use QUERY instead", y=290)
    bar(base, F_GS, 620, w=1010, colors=[("A1:B9", C_A)], t=t, t0=0.25, cps=44)
    info_rows(base, t, 1.35, [("Older Excel: use a PivotTable", None)], y0=900, size=42)
    a = ease(seg(t, 0.2, 0.5))
    src = Sheet(0, 1010, [200, 160], [["Region", "Sales"]] + [[r, str(v)] for r, v in SALES], row_h=52)
    src.x = (W - src.width()) // 2
    src.draw(base, a=a, fills=src_fills() if t >= 0.6 else None, font_size=32)
    src.outline(base, [src.col_x(0), src.cell_box(0, 0)[1], src.col_x(1) + 160, src.cell_box(8, 1)[3]], C_A,
                a=a * ease(seg(t, 0.5, 0.7)), width=6)
    return base

QUESTION = "PivotTable or GROUPBY?"

def sc_outro(t, D):
    return loop_back(outro(t, question=QUESTION), sc_hook(0.0, 2.4), t, D, dur=0.35)

SCENES = [
    ("01_hook", sc_hook, 2.4),
    ("02_problem", sc_problem, 2.2),
    ("03_fix", sc_fix, 2.8),
    ("04_how", sc_how, 2.6),
    ("05_sheets", sc_sheets, 2.4),
    ("06_outro", sc_outro, 3.2),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        out = os.path.join(HERE, "stills"); os.makedirs(out, exist_ok=True)
        stills(SCENES, out, fracs=(0.0, 0.5, 0.95))
        print(sum(D for *_, D in SCENES), "| hook font", HF.size, "| T_FIX", round(T_FIX, 2))
        sys.exit()
    starts, total = scene_starts(SCENES)
    wav = os.path.join(HERE, "music.wav")
    style, seed = music_styles.pick_style(f"{DATE}-{SLUG}")
    lufs = music_upbeat.make_track(total, cuts=starts[1:], out_wav=wav, style=style, seed=seed,
                                   impacts=[0.0, starts[0] + 0.85, starts[1] + 1.25, starts[2] + T_FIX])
    print("music", style, seed, "LUFS", round(lufs, 2), "duration", total)
    render_all(SCENES, os.path.join(HERE, "work"), os.path.join(HERE, f"{SLUG}.mp4"), wav)
    sc_hook(2.0, 2.4).convert("RGB").save(os.path.join(HERE, "cover.jpg"), quality=92)
