"""Opening formats for @cellbycell1 Reels (added 2026-11-26, hook test).

Why: with the amber-headline title card ~87% of viewers swipe away in the first 3 s. That opening looks like an ad
slide: a big headline, a small table, a lot of empty navy. These three openings start INSIDE the action instead.

    cold_open   full-screen sheet, something already going wrong/right at frame 0, small caption sticker
    chat_open   a message from a boss/coworker creates the stakes, the sheet answers it
    quiz_open   "A or B?" with a countdown, the answer lands at ~1.8 s

Building blocks (compose them in the Reel's sc_hook; see tools/hook_demo.py for one full example of each):
    screen_bg()                      light "you are inside the spreadsheet" canvas (use instead of background())
    big_sheet(data, col_w, y)        a Sheet scaled to fill the screen width (big, phone-readable cells)
    sticker(base, lines, cy, t, t0)  caption box in the native "text sticker" look (white box, dark text)
    chat_bubble / typing_dots        message bubbles
    quiz_cards(...)                  A/B cards + countdown bar + reveal
    camera(frame, t, t0, t1, z0, z1, focus)   slow push-in / pull-out so the frame moves from t=0

Rules for every opening: motion from frame 0, the sheet covers at least half of the screen, at most ONE short text
block in the first second (max 6 words), no formula text before the result, keep text inside SAFE_TOP..SAFE_BOTTOM.
"""
from engine import *
from PIL import Image, ImageDraw, ImageFilter

PAPER = (243, 246, 250)
INK = (22, 30, 46)
SOFT = (226, 232, 241)


# ---------- canvas ----------
_sbg = None
def screen_bg():
    """Light canvas with a faint cell grid: reads as "zoomed into a real sheet", not as a title card."""
    global _sbg
    if _sbg is None:
        im = Image.new("RGBA", (W, H), PAPER + (255,))
        d = ImageDraw.Draw(im)
        for x in range(0, W, 180): d.line([(x, 0), (x, H)], fill=SOFT, width=2)
        for y in range(0, H, 96): d.line([(0, y), (W, y)], fill=SOFT, width=2)
        _sbg = im
    return _sbg.copy()


def big_sheet(data, col_w, y=520, row_h=132, margin=30):
    """Sheet whose columns are scaled so the table spans the screen width. col_w = relative widths."""
    s = Sheet(0, y, list(col_w), data, row_h=row_h)
    k = (W - 2 * margin - s.num_w) / float(sum(col_w))
    s.col_w = [int(c * k) for c in col_w]
    s.x = (W - s.width()) // 2
    return s


def camera(frame, t, t0=0.0, t1=1.2, z0=1.12, z1=1.0, focus=(0.5, 0.5)):
    """Zoom between z0 and z1 around `focus` (fractions of the frame). z > 1 = closer. Gives motion from frame 0."""
    z = z0 + (z1 - z0) * ease_io(seg(t, t0, t1))
    if abs(z - 1) < 0.002: return frame
    w, h = W / z, H / z
    x0 = clamp(focus[0] * W - w / 2, 0, W - w); y0 = clamp(focus[1] * H - h / 2, 0, H - h)
    return frame.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BICUBIC)


# ---------- caption sticker ----------
def sticker(base, lines, cy, t, t0=0.0, size=64, bg=WHITE, fg=INK, hot=None, hot_col=RED, pad=(44, 26), dur=0.28):
    """Caption box like a native text sticker. lines: 1-2 short strings. hot: a word to color (e.g. "#REF!").
    Pops in at t0 (already 85% size at t0 so the first frame is never empty when t0 <= 0)."""
    if isinstance(lines, str): lines = [lines]
    p = back(seg(t, t0, t0 + dur))
    if t < t0: return
    f = F("Bold", size)
    lh = int(size * 1.28)
    tw = max(f.getlength(l) for l in lines)
    while tw > W - 150 and size > 40:
        size -= 2; f = F("Bold", size); lh = int(size * 1.28); tw = max(f.getlength(l) for l in lines)
    bw, bh = int(tw + pad[0] * 2), int(lh * len(lines) + pad[1] * 2)
    lay = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([20, 26, 20 + bw, 26 + bh], 30, fill=(10, 20, 40, 70))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 20 + bw, 20 + bh], 30, fill=bg + (255,))
    for i, l in enumerate(lines):
        y = 20 + pad[1] + i * lh + lh / 2
        if hot and hot in l:
            a, b = l.split(hot, 1)
            x = 20 + (bw - f.getlength(l)) / 2
            d.text((x, y), a, font=f, fill=fg, anchor="lm"); x += f.getlength(a)
            d.text((x, y), hot, font=f, fill=hot_col, anchor="lm"); x += f.getlength(hot)
            d.text((x, y), b, font=f, fill=fg, anchor="lm")
        else:
            d.text((20 + bw / 2, y), l, font=f, fill=fg, anchor="mm")
    sc = 0.85 + 0.15 * p
    l2 = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.BICUBIC)
    base.alpha_composite(l2, (int(W / 2 - l2.width / 2), int(cy - l2.height / 2)))


# ---------- chat ----------
def chat_bubble(base, text, y, t, t0=0.0, who=None, side="left", size=54, col=None, max_w=760):
    """Message bubble. side "left" = incoming (white), "right" = you (amber). Returns the bubble's bottom y."""
    f = F("Medium", size); fb = F("Bold", 34)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        nx = (cur + " " + w_).strip()
        if f.getlength(nx) <= max_w - 80: cur = nx
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    lh = int(size * 1.3)
    bw = int(max(f.getlength(l) for l in lines) + 80); bh = lh * len(lines) + 50
    top = y + (40 if who else 0)
    if t < t0: return top + bh
    p = back(seg(t, t0, t0 + 0.3))
    bg = col or (WHITE if side == "left" else AMBER)
    x0 = 60 if side == "left" else W - 60 - bw
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    off = int((1 - p) * 50)
    if who: d.text((x0 + 14, y + 14 + off), who, font=fb, fill=(110, 124, 150), anchor="lm")
    d.rounded_rectangle([x0 + 4, top + 8 + off, x0 + bw + 4, top + bh + 8 + off], 40, fill=(10, 20, 40, 40))
    d.rounded_rectangle([x0, top + off, x0 + bw, top + bh + off], 40, fill=bg + (255,))
    for i, l in enumerate(lines):
        d.text((x0 + 40, top + 25 + i * lh + lh / 2 + off), l, font=f, fill=INK, anchor="lm")
    if p < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * clamp(0.4 + p))))
    base.alpha_composite(lay)
    return top + bh


def typing_dots(base, y, t, t0, t1, side="left"):
    """Three bouncing dots in a small bubble between t0 and t1."""
    if not (t0 <= t < t1): return
    x0 = 60 if side == "left" else W - 60 - 190
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x0, y, x0 + 190, y + 96], 44, fill=WHITE)
    for i in range(3):
        dy = -10 * max(0.0, math.sin((t - t0) * 9 - i * 0.9))
        cx = x0 + 52 + i * 44
        d.ellipse([cx - 13, y + 48 - 13 + dy, cx + 13, y + 48 + 13 + dy], fill=(150, 162, 186))


# ---------- quiz ----------
def quiz_cards(base, t, a, b, correct, y=1010, t_in=0.0, t_reveal=1.8, h=250, size=88):
    """Two answer cards (A left, B right) + a countdown bar that runs out at t_reveal, then the reveal:
    the right card turns green with a check, the wrong one fades red with a cross. correct: "a" or "b".
    Returns the frame offset (dx) to apply for the reveal shake via engine.shake()."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    gap, m = 36, 50
    cw = (W - 2 * m - gap) // 2
    rv = seg(t, t_reveal, t_reveal + 0.25)
    for i, (key, txt) in enumerate((("a", a), ("b", b))):
        p = back(seg(t, t_in + i * 0.08, t_in + 0.32 + i * 0.08))
        x0 = m + i * (cw + gap); yo = y + int((1 - p) * 70)
        ok = key == correct
        if rv > 0:
            bg = GREEN if ok else (250, 222, 223)
            fg = WHITE if ok else (150, 80, 84)
        else:
            bg, fg = WHITE, INK
        d.rounded_rectangle([x0 + 6, yo + 10, x0 + cw + 6, yo + h + 10], 44, fill=(10, 20, 40, 45))
        d.rounded_rectangle([x0, yo, x0 + cw, yo + h], 44, fill=bg + (255,),
                            outline=(AMBER if rv == 0 else (GREEN if ok else RED)) + (255,), width=8)
        d.ellipse([x0 + 26, yo + 26, x0 + 98, yo + 98], fill=(AMBER if rv == 0 else (WHITE if ok else RED)) + (255,))
        d.text((x0 + 62, yo + 62), key.upper(), font=F("Bold", 44), fill=(INK if rv == 0 or ok else WHITE), anchor="mm")
        f = fit_font("Bold", txt, cw - 70, size, 44)
        d.text((x0 + cw / 2, yo + h / 2 + 26), txt, font=f, fill=fg, anchor="mm")
        if rv > 0:
            r = int(44 * back(rv)); cx, cy = x0 + cw - 62, yo + 62
            if ok:
                d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE)
                d.line([(cx - r * .45, cy), (cx - r * .1, cy + r * .38), (cx + r * .5, cy - r * .35)], fill=GREEN, width=10, joint="curve")
            else:
                d.line([(cx - r * .5, cy - r * .5), (cx + r * .5, cy + r * .5)], fill=RED, width=12)
                d.line([(cx - r * .5, cy + r * .5), (cx + r * .5, cy - r * .5)], fill=RED, width=12)
    # countdown bar
    if t < t_reveal:
        k = 1 - seg(t, t_in + 0.2, t_reveal)
        by = y + h + 60
        d.rounded_rectangle([m, by, W - m, by + 22], 11, fill=(205, 213, 226, 255))
        if k > 0.02: d.rounded_rectangle([m, by, m + int((W - 2 * m) * k), by + 22], 11, fill=AMBER + (255,))
    base.alpha_composite(lay)


def shake_bg(frame, t, t0, dur=0.25, amp=14, col=PAPER):
    """engine.shake() for light canvases (fills the uncovered edge with `col` instead of navy)."""
    p = seg(t, t0, t0 + dur)
    if p <= 0 or p >= 1: return frame
    dx = int(math.sin(p * 40) * amp * (1 - p))
    out = Image.new("RGBA", (W, H), col + (255,)); out.alpha_composite(frame.convert("RGBA"), (dx, 0))
    return out
