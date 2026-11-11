"""@cellbycell1 Reels engine: brand constants, easing, spreadsheet drawing, cards, render + mux.

Reuse and extend this file for every Reel; do not rewrite it per video.
"""
import math, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SAFE_TOP, SAFE_BOTTOM = 250, H - 350   # keep text between these (Instagram UI)

FD = "/usr/share/fonts/truetype/google-fonts/"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SYM = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"   # arrows, vertical ellipsis, Cmd sign (not in Poppins)
SYM_CHARS = set("\u2190\u2191\u2192\u2193\u22ee\u2318")       # ← ↑ → ↓ ⋮ ⌘
_fc = {}
def F(w, s):
    """w: Poppins weight ("Bold", "Medium", ...), "Mono" (formulas) or "Sym" (arrow glyphs)."""
    k = (w, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(MONO if w == "Mono" else SYM if w == "Sym" else FD + f"Poppins-{w}.ttf", s)
    return _fc[k]
def needs_sym(s): return any(ch in SYM_CHARS for ch in s)

# ---------- brand ----------
NAVY = (19, 35, 63)        # background
NAVY2 = (38, 56, 90)       # empty cells / panels
NAVY3 = (58, 78, 116)      # grid lines
AMBER = (255, 176, 32)     # highlight / brand accent
WHITE = (255, 255, 255)
MUTED = (170, 184, 210)
GREEN = (34, 176, 112)     # do / correct
RED = (234, 72, 77)        # don't / wrong
BLUE = (88, 160, 255)      # second range highlight

# ---------- easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_io(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def seg(t, a, b): return clamp((t - a) / (b - a))

def rgba(c, a): return tuple(c[:3]) + (int(clamp(a) * 255),)

# ---------- background ----------
_bg = None
def background():
    """Navy background with a faint spreadsheet grid."""
    global _bg
    if _bg is None:
        im = Image.new("RGBA", (W, H), NAVY + (255,))
        d = ImageDraw.Draw(im)
        for x in range(0, W, 120): d.line([(x, 0), (x, H)], fill=(28, 46, 78), width=2)
        for y in range(0, H, 60): d.line([(0, y), (W, y)], fill=(28, 46, 78), width=2)
        _bg = im
    return _bg.copy()

# ---------- text helpers ----------
def text_center(d, xy, s, font, fill, stroke=0, stroke_fill=NAVY):
    d.text(xy, s, font=font, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=stroke_fill)

def pop_text(base, s, cx, cy, font, fill, t, t0, stroke=8, dur=0.35):
    """Text that pops in with an overshoot scale."""
    p = seg(t, t0, t0 + dur)
    if p <= 0: return
    sc = back(p)
    tw = int(font.getlength(s)) + stroke * 2 + 40
    th = font.size + stroke * 2 + 60
    lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((tw // 2, th // 2), s, font=font, fill=fill, anchor="mm",
                             stroke_width=stroke, stroke_fill=NAVY)
    nw, nh = max(1, int(tw * sc)), max(1, int(th * sc))
    lay = lay.resize((nw, nh), Image.LANCZOS)
    base.alpha_composite(lay, (int(cx - nw / 2), int(cy - nh / 2)))

def pill(d, cx, cy, s, bg, fg=WHITE, size=40, a=1.0):
    f = F("Bold", size)
    w = f.getlength(s) + size * 1.4
    h = size * 1.8
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h / 2, fill=rgba(bg, a))
    d.text((cx, cy), s, font=f, fill=rgba(fg, a), anchor="mm")

def label_card(base, t, t0, tag, tag_col, title, y=300, sub=None):
    """Top card: colored tag pill + big title (+ optional subtitle). Slides in."""
    p = ease(seg(t, t0, t0 + 0.4))
    if p <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    dy = (1 - p) * 60
    pill(d, W / 2, y + dy, tag, tag_col, size=38, a=p)
    fT = F("Bold", 76)
    lines = title.split("\n")
    for i, ln in enumerate(lines):
        d.text((W / 2, y + 120 + i * 92 + dy), ln, font=fT, fill=rgba(WHITE, p), anchor="mm")
    if sub:
        d.text((W / 2, y + 120 + len(lines) * 92 + 10 + dy), sub, font=F("Medium", 42), fill=rgba(MUTED, p), anchor="mm")
    base.alpha_composite(lay)

def check_icon(d, cx, cy, r, col=GREEN, a=1.0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(col, a))
    w = max(4, int(r * 0.22))
    d.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.12, cy + r * 0.35), (cx + r * 0.48, cy - r * 0.35)],
           fill=rgba(WHITE, a), width=w, joint="curve")

def cross_icon(d, cx, cy, r, col=RED, a=1.0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(col, a))
    w = max(4, int(r * 0.22)); k = r * 0.38
    d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=rgba(WHITE, a), width=w)
    d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=rgba(WHITE, a), width=w)

def arrow(d, x0, y0, x1, y1, col, width=12, head=34, a=1.0):
    d.line([(x0, y0), (x1, y1)], fill=rgba(col, a), width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    p1 = (x1 - head * math.cos(ang - 0.5), y1 - head * math.sin(ang - 0.5))
    p2 = (x1 - head * math.cos(ang + 0.5), y1 - head * math.sin(ang + 0.5))
    d.polygon([(x1, y1), p1, p2], fill=rgba(col, a))

# ---------- spreadsheet ----------
class Sheet:
    """A small spreadsheet: column letters, row numbers, cells.

    cols: list of column widths (px). rows: list of lists of cell strings (row 0 = header row of the data).
    """
    def __init__(self, x, y, col_w, data, row_h=92, letters=None, row_labels=None):
        """row_labels: optional list of row-number strings (e.g. ["1", "2", "\u22ee", "5000"]) for big/scrolled sheets."""
        self.x, self.y, self.col_w, self.data, self.row_h = x, y, col_w, data, row_h
        self.letters = letters or [chr(65 + i) for i in range(len(col_w))]
        self.row_labels = row_labels
        self.hdr_h, self.num_w = 58, 64
        if row_labels:   # widen the row-number column for long labels like "5000"
            self.num_w = max(64, int(max(F("Bold", 26).getlength(l) for l in row_labels) + 34))

    def width(self): return self.num_w + sum(self.col_w)
    def height(self): return self.hdr_h + self.row_h * len(self.data)

    def col_x(self, c):
        return self.x + self.num_w + sum(self.col_w[:c])

    def cell_box(self, r, c):
        x0 = self.col_x(c); y0 = self.y + self.hdr_h + r * self.row_h
        return [x0, y0, x0 + self.col_w[c], y0 + self.row_h]

    def col_box(self, c, r0=1, r1=None):
        r1 = len(self.data) - 1 if r1 is None else r1
        b0, b1 = self.cell_box(r0, c), self.cell_box(r1, c)
        return [b0[0], b0[1], b1[2], b1[3]]

    def draw(self, base, a=1.0, fills=None, text_cols=None, font_size=40, checks=None, strike=None):
        """fills: {(r,c): color} cell tints. text_cols: {(r,c): color} text color overrides.
        checks: {(r,c): 0..1} draw an in-cell checkbox (0 = empty, 1 = ticked) instead of the text.
        strike: {(r,c): 0..1} strikethrough line across the cell text, growing left to right."""
        fills = fills or {}; text_cols = text_cols or {}; checks = checks or {}; strike = strike or {}
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        x, y = self.x, self.y
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([x, y + 16, x + self.width(), y + self.height() + 16], 26, fill=(0, 0, 0, int(120 * a)))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
        d.rounded_rectangle([x, y, x + self.width(), y + self.height()], 26, fill=rgba((250, 251, 253), a))
        # header strip
        d.rounded_rectangle([x, y, x + self.width(), y + self.hdr_h + 26], 26, fill=rgba((226, 231, 240), a))
        d.rectangle([x, y + self.hdr_h, x + self.width(), y + self.hdr_h + 26], fill=rgba((250, 251, 253), a))
        d.rectangle([x, y + self.hdr_h, x + self.num_w, y + self.height() - 26], fill=rgba((226, 231, 240), a))
        d.rounded_rectangle([x, y + self.height() - 52, x + self.num_w, y + self.height()], 26, fill=rgba((226, 231, 240), a))
        d.rectangle([x + 26, y + self.height() - 52, x + self.num_w, y + self.height()], fill=rgba((226, 231, 240), a))
        fh = F("Bold", 30)
        for c, L in enumerate(self.letters):
            cx = self.col_x(c) + self.col_w[c] / 2
            d.text((cx, y + self.hdr_h / 2), L, font=fh, fill=rgba((96, 108, 130), a), anchor="mm")
        for r in range(len(self.data)):
            cy = y + self.hdr_h + r * self.row_h + self.row_h / 2
            lab = self.row_labels[r] if self.row_labels else str(r + 1)
            fl = F("Sym", 30) if needs_sym(lab) else F("Bold", 30 if len(lab) < 4 else 26)
            d.text((x + self.num_w / 2, cy), lab, font=fl, fill=rgba((96, 108, 130), a), anchor="mm")
        for (r, c), col in fills.items():
            b = self.cell_box(r, c)
            d.rectangle(b, fill=rgba(col, a))
        # grid
        for c in range(len(self.col_w) + 1):
            gx = self.col_x(c) if c < len(self.col_w) else x + self.width()
            if c == len(self.col_w): continue
            d.line([(gx, y), (gx, y + self.height())], fill=rgba((206, 213, 225), a), width=2)
        for r in range(len(self.data) + 1):
            gy = y + self.hdr_h + r * self.row_h
            d.line([(x, gy), (x + self.width(), gy)], fill=rgba((206, 213, 225), a), width=2)
        for (r, c), on in checks.items():
            b = self.cell_box(r, c); bx = min(52, self.row_h * 0.56)
            cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
            sc = 1 + 0.18 * math.sin(math.pi * clamp(on))
            k = bx * sc / 2
            d.rounded_rectangle([cx - k, cy - k, cx + k, cy + k], 9, outline=rgba((120, 132, 156) if on < 0.5 else GREEN, a),
                                width=4, fill=rgba(GREEN, a * clamp(on * 2)) if on > 0 else rgba(WHITE, a))
            if on > 0.35:
                q = clamp((on - 0.35) / 0.65)
                p0, p1, p2 = (cx - k * 0.5, cy + 1), (cx - k * 0.12, cy + k * 0.42), (cx + k * 0.55, cy - k * 0.45)
                if q < 0.4:
                    e = q / 0.4; d.line([p0, (p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e)], fill=rgba(WHITE, a), width=6)
                else:
                    e = (q - 0.4) / 0.6
                    d.line([p0, p1, (p1[0] + (p2[0] - p1[0]) * e, p1[1] + (p2[1] - p1[1]) * e)], fill=rgba(WHITE, a), width=6, joint="curve")
        for r, row in enumerate(self.data):
            for c, s in enumerate(row):
                if not s or (r, c) in checks: continue
                b = self.cell_box(r, c)
                bold = r == 0 and not self.row_labels or (self.row_labels and self.row_labels[r] == "1")
                f = F("Bold" if bold else "Medium", font_size if not bold else font_size - 4)
                if needs_sym(s): f = F("Sym", font_size)
                col = text_cols.get((r, c), (30, 40, 60) if not bold else (70, 82, 104))
                d.text((b[0] + 22, (b[1] + b[3]) / 2), s, font=f, fill=rgba(col, a), anchor="lm")
                sp = clamp(strike.get((r, c), 0))
                if sp > 0:
                    cy = (b[1] + b[3]) / 2 + 2
                    d.line([(b[0] + 16, cy), (b[0] + 16 + (f.getlength(s) + 12) * sp, cy)], fill=rgba(col, a), width=5)
        base.alpha_composite(lay)

    def outline(self, base, box, col, a=1.0, width=8, dash=False):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle([box[0] - 4, box[1] - 4, box[2] + 4, box[3] + 4], 10, outline=rgba(col, a), width=width)
        base.alpha_composite(lay)

def formula_bar(base, x, y, w, text, t=None, t0=0.0, cps=28, a=1.0, colors=None, size=46):
    """A formula bar with an 'fx' tag; text types on from t0 at cps chars/s when t is given.
    colors: list of (substring, color) to tint parts of the formula."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    h = 104
    d.rounded_rectangle([x, y, x + w, y + h], 24, fill=rgba(WHITE, a))
    d.rounded_rectangle([x + 14, y + 16, x + 92, y + h - 16], 16, fill=rgba(NAVY2, a))
    d.text((x + 53, y + h / 2), "fx", font=F("Bold", 34), fill=rgba(AMBER, a), anchor="mm")
    n = len(text) if t is None else int(clamp((t - t0) * cps, 0, len(text)))
    shown = text[:n]
    f = F("Mono", size)
    # colorize by spans
    spans = [(0, len(text), (30, 40, 60))]
    if colors:
        spans = []
        i = 0
        marks = []
        for sub, col in colors:
            k = text.find(sub)
            if k >= 0: marks.append((k, k + len(sub), col))
        marks.sort()
        for k0, k1, col in marks:
            if k0 > i: spans.append((i, k0, (30, 40, 60)))
            spans.append((k0, k1, col)); i = k1
        if i < len(text): spans.append((i, len(text), (30, 40, 60)))
    cx = x + 118
    for k0, k1, col in spans:
        part = shown[k0:k1] if k0 < n else ""
        if part:
            d.text((cx, y + h / 2), part, font=f, fill=rgba(col, a), anchor="lm")
        cx += f.getlength(text[k0:k1])
    # caret
    if t is not None and n < len(text) and int(t * 4) % 2 == 0:
        ccx = x + 118 + f.getlength(shown)
        d.line([(ccx + 2, y + 26), (ccx + 2, y + h - 26)], fill=rgba(NAVY, a), width=4)
    base.alpha_composite(lay)
    return h

def result_chip(base, cx, cy, s, ok, t, t0):
    """Big result chip with check or cross that pops in."""
    p = seg(t, t0, t0 + 0.35)
    if p <= 0: return
    sc = back(p)
    f = F("Bold", 54)
    w = f.getlength(s) + 190; h = 120
    lay = Image.new("RGBA", (int(w) + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    col = GREEN if ok else RED
    d.rounded_rectangle([20, 20, 20 + w, 20 + h], h / 2, fill=col + (255,))
    (check_icon if ok else cross_icon)(d, 20 + 62, 20 + h / 2, 38, col=WHITE)
    # redraw glyph in the brand color on white disc
    d.ellipse([20 + 24, 20 + h / 2 - 38, 20 + 100, 20 + h / 2 + 38], fill=WHITE)
    (check_icon if ok else cross_icon)(d, 20 + 62, 20 + h / 2, 30, col=col)
    d.text((20 + 124, 20 + h / 2), s, font=f, fill=WHITE, anchor="lm")
    nw, nh = int(lay.width * sc), int(lay.height * sc)
    lay = lay.resize((max(1, nw), max(1, nh)), Image.LANCZOS)
    base.alpha_composite(lay, (int(cx - nw / 2), int(cy - nh / 2)))

def punch(frame, t, t0=0.0, amt=0.06, dur=0.5):
    """Punch-in zoom: starts zoomed amt and settles to 1.0."""
    p = ease(seg(t, t0, t0 + dur))
    s = 1 + amt * (1 - p)
    if s <= 1.0005: return frame
    nw, nh = int(W * s), int(H * s)
    big = frame.resize((nw, nh), Image.BILINEAR)
    return big.crop(((nw - W) // 2, (nh - H) // 2, (nw - W) // 2 + W, (nh - H) // 2 + H))

def shake(frame, t, t0, dur=0.25, amp=14):
    p = seg(t, t0, t0 + dur)
    if p <= 0 or p >= 1: return frame
    dx = int(math.sin(p * 40) * amp * (1 - p))
    out = Image.new("RGBA", (W, H), NAVY + (255,)); out.alpha_composite(frame, (dx, 0))
    return out

def outro(t, handle="@cellbycell1", line1="Save this for", line2="your next spreadsheet!"):
    base = background()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    p = ease(seg(t, 0.05, 0.5))
    top = 560 + (1 - p) * 60
    d.rounded_rectangle([70, top, W - 70, top + 660], 56, fill=rgba(AMBER, p))
    a = p
    bx, by = W / 2, top + 140
    d.polygon([(bx - 48, by - 70), (bx + 48, by - 70), (bx + 48, by + 70), (bx, by + 30), (bx - 48, by + 70)], fill=rgba(NAVY, a))
    d.text((W / 2, top + 290), line1, font=F("Bold", 74), fill=rgba(NAVY, a), anchor="mm")
    d.text((W / 2, top + 380), line2, font=F("Bold", 64), fill=rgba(NAVY, a), anchor="mm")
    q = ease(seg(t, 0.8, 1.3))
    d.rounded_rectangle([W / 2 - 300, top + 480, W / 2 + 300, top + 590], 55, fill=rgba(NAVY, q))
    d.text((W / 2, top + 535), f"Follow {handle}", font=F("Bold", 44), fill=rgba(WHITE, q), anchor="mm")
    base.alpha_composite(lay)
    return base

# ---------- render ----------
def render_scene(scene, outdir):
    name, fn, D = scene
    n = int(round(D * FPS))
    out = os.path.join(outdir, f"{name}.mp4"); tmp = out[:-4] + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
           "-pix_fmt", "yuv420p", "-r", str(FPS), tmp]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        pr.stdin.write(fn(k / FPS, D).convert("RGB").tobytes())
    pr.stdin.close()
    if pr.wait() != 0: raise RuntimeError(f"ffmpeg failed for {name}")
    os.replace(tmp, out)
    return name

def stills(scenes, outdir, fracs=(0.5, 0.95)):
    os.makedirs(outdir, exist_ok=True)
    for name, fn, D in scenes:
        for fr in fracs:
            fn(D * fr, D).convert("RGB").save(os.path.join(outdir, f"{name}_{int(fr*100)}.jpg"), quality=85)

def render_all(scenes, workdir, final_mp4, audio_wav, procs=2):
    from multiprocessing import Pool
    from functools import partial
    os.makedirs(workdir, exist_ok=True)
    with Pool(procs) as p:
        for r in p.imap_unordered(partial(render_scene, outdir=workdir), scenes): print("done", r, flush=True)
    lst = os.path.join(workdir, "list.txt")
    with open(lst, "w") as f:
        for name, _, _ in scenes: f.write(f"file '{os.path.join(workdir, name)}.mp4'\n")
    silent = os.path.join(workdir, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", silent], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio_wav, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", final_mp4], check=True)

def scene_starts(scenes):
    out, t = [], 0.0
    for _, _, D in scenes: out.append(t); t += D
    return out, t

# ---------- menus & dialogs (drawn, generic; never product screenshots) ----------
def menu_path(base, t, t0, steps, y, size=36, gap=0.45, col=NAVY2, hot=AMBER, max_w=W - 120):
    """Menu path as pills joined by chevrons ("Data" > "Remove Duplicates").
    Steps pop in one after another (gap s); the newest step flashes amber with a click ring.
    Wraps onto a second row when wider than max_w. Returns the time the last step appears."""
    f = F("Bold", size)
    ws = [f.getlength(s) + size * 1.4 for s in steps]
    chev = size * 1.3
    rows, cur, cw = [], [], 0
    for i, w in enumerate(ws):
        add = w + (chev if cur else 0)
        if cur and cw + add > max_w:
            rows.append(cur); cur, cw = [], 0; add = w
        cur.append(i); cw += add
    rows.append(cur)
    h = size * 1.8
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for ri, idx in enumerate(rows):
        tot = sum(ws[i] for i in idx) + chev * (len(idx) - 1)
        x = (W - tot) / 2; cy = y + ri * (h + 26)
        for j, i in enumerate(idx):
            ti = t0 + i * gap
            p = ease(seg(t, ti, ti + 0.25))
            if j > 0 or ri > 0:
                if j > 0:
                    ca = p
                    cx0 = x - chev / 2
                    d.line([(cx0 - 8, cy - 14), (cx0 + 8, cy), (cx0 - 8, cy + 14)], fill=rgba(MUTED, ca), width=6, joint="curve")
            if p > 0:
                active = t < ti + 0.45 or i == len(steps) - 1
                bg = hot if active else col
                fg = NAVY if active else WHITE
                sc = back(seg(t, ti, ti + 0.25))
                ww, hh = ws[i] * sc, h * sc
                cx = x + ws[i] / 2
                d.rounded_rectangle([cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2], hh / 2, fill=rgba(bg, p))
                d.text((cx, cy), steps[i], font=F("Bold", max(8, int(size * sc))), fill=rgba(fg, p), anchor="mm")
                q = seg(t, ti + 0.15, ti + 0.55)
                if 0 < q < 1:
                    r = 20 + 70 * ease(q)
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=rgba(WHITE, 1 - q), width=6)
            x += ws[i] + chev
    base.alpha_composite(lay)
    return t0 + gap * (len(steps) - 1)

def checkbox(d, x, y, s, on, a=1.0, size=40, box=46):
    """Checkbox + label at (x, y=center). on: 0..1 fill progress."""
    d.rounded_rectangle([x, y - box / 2, x + box, y + box / 2], 10, outline=rgba((120, 132, 156), a), width=4,
                        fill=rgba(GREEN, a * on) if on > 0 else None)
    if on > 0.3:
        d.line([(x + box * 0.22, y + 1), (x + box * 0.43, y + box * 0.24), (x + box * 0.8, y - box * 0.24)],
               fill=rgba(WHITE, a), width=6, joint="curve")
    d.text((x + box + 24, y), s, font=F("Medium", size), fill=rgba((30, 40, 60), a), anchor="lm")

def dialog(base, t, t0, title, items, button, y=720, w=760, t_out=None, tick_gap=0.2, press=None):
    """Generic modal dialog: title, checkbox rows (ticked one by one from t0+0.35), and a button.
    press: time the button is pressed (flash). t_out: time it fades out."""
    p = ease(seg(t, t0, t0 + 0.3))
    if t_out is not None: p *= 1 - ease(seg(t, t_out, t_out + 0.25))
    if p <= 0: return
    dim = Image.new("RGBA", (W, H), (10, 18, 34, int(130 * p))); base.alpha_composite(dim)
    sc = 0.9 + 0.1 * back(seg(t, t0, t0 + 0.3))
    hgt = 130 + len(items) * 84 + 150
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0 = (W - w) / 2
    d.rounded_rectangle([x0, y, x0 + w, y + hgt], 30, fill=rgba(WHITE, p))
    d.rounded_rectangle([x0, y, x0 + w, y + 100], 30, fill=rgba((226, 231, 240), p))
    d.rectangle([x0, y + 70, x0 + w, y + 100], fill=rgba((226, 231, 240), p))
    d.text((x0 + 40, y + 52), title, font=F("Bold", 40), fill=rgba((40, 52, 76), p), anchor="lm")
    for i, s in enumerate(items):
        on = ease(seg(t, t0 + 0.35 + i * tick_gap, t0 + 0.5 + i * tick_gap))
        checkbox(d, x0 + 50, y + 150 + i * 84, s, on, a=p)
    bf = F("Bold", 38); bw = bf.getlength(button) + 80
    by = y + hgt - 85
    pr = 0 if press is None else seg(t, press, press + 0.25)
    bcol = GREEN if 0 < pr else (40, 110, 220)
    d.rounded_rectangle([x0 + w - 40 - bw, by - 40, x0 + w - 40, by + 40], 40, fill=rgba(bcol, p))
    d.text((x0 + w - 40 - bw / 2, by), button, font=bf, fill=rgba(WHITE, p), anchor="mm")
    if 0 < pr < 1:
        cx = x0 + w - 40 - bw / 2; r = 30 + 70 * ease(pr)
        d.ellipse([cx - r, by - r, cx + r, by + r], outline=rgba(AMBER, 1 - pr), width=6)
    if sc < 0.999:
        lay = lay.resize((int(W * sc), int(H * sc)), Image.BILINEAR)
        full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        full.alpha_composite(lay, (int((W - lay.width) / 2), int((H - lay.height) / 2 + (y + hgt / 2 - H / 2) * (1 - sc))))
        lay = full
    base.alpha_composite(lay)

def strike_rows(base, sheet, rows, t, t0, col=RED, width=8):
    """Draw a strike-through line across whole rows of a Sheet, growing from t0."""
    p = ease(seg(t, t0, t0 + 0.3))
    if p <= 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for r in rows:
        b0 = sheet.cell_box(r, 0); b1 = sheet.cell_box(r, len(sheet.col_w) - 1)
        cy = (b0[1] + b0[3]) / 2
        d.line([(b0[0] + 10, cy), (b0[0] + 10 + (b1[2] - b0[0] - 20) * p, cy)], fill=rgba(col, 1), width=width)
    base.alpha_composite(lay)

# ---------- keyboard shortcuts ----------
SEP_WORDS = ("then", "+")
def keycaps(base, t, t0, keys, cy, size=40, gap=0.22, cx=W / 2, a=1.0, hot=AMBER):
    """Keyboard combo drawn as keycaps, e.g. ["Ctrl", "+", "Shift", "+", ";"] or with "then" between steps.
    Caps pop in one by one (gap s) and get a press dip; "+" and "then" are drawn as plain separators.
    Pressed caps turn amber. Returns the time the last cap is pressed."""
    f = F("Bold", size); fs = F("Bold", int(size * 0.8)); fthen = F("Medium", int(size * 0.72))
    ch = size * 2.0; pad = size * 0.7
    items = []
    for k in keys:
        if k == "+": items.append(("plus", k, fs.getlength("+") + size * 0.6))
        elif k == "then": items.append(("then", k, fthen.getlength("then") + size * 0.7))
        else: items.append(("cap", k, max(ch, f.getlength(k) + pad * 2)))
    tot = sum(w for *_, w in items)
    x = cx - tot / 2
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ci = 0; last = t0
    for kind, s, w in items:
        if kind == "cap":
            ti = t0 + ci * gap; last = ti; ci += 1
            fk = F("Sym", int(size * 1.15)) if needs_sym(s) else f
            p = ease(seg(t, ti - 0.12, ti + 0.08))
            if p > 0:
                dip = 10 * math.sin(math.pi * seg(t, ti, ti + 0.18))
                pressed = t >= ti
                top = cy - ch / 2 + dip + (1 - p) * 30
                d.rounded_rectangle([x, cy - ch / 2 + 12 + (1 - p) * 30, x + w, cy + ch / 2 + 12 + (1 - p) * 30], 18,
                                    fill=rgba((150, 104, 10) if pressed else (12, 22, 42), a * p))
                d.rounded_rectangle([x, top, x + w, top + ch], 18, fill=rgba(hot if pressed else WHITE, a * p))
                d.text((x + w / 2, top + ch / 2), s, font=fk, fill=rgba(NAVY, a * p), anchor="mm")
        else:
            p = ease(seg(t, t0 + (ci - 0.5) * gap - 0.1, t0 + (ci - 0.5) * gap + 0.1))
            if p > 0:
                fo = fs if kind == "plus" else fthen
                d.text((x + w / 2, cy + 6), s, font=fo, fill=rgba(MUTED if kind == "then" else WHITE, a * p), anchor="mm")
        x += w
    base.alpha_composite(lay)
    return last

def info_rows(base, t, t0, items, y0=760, step=170, gap=0.3, size=46):
    """Stacked navy rows with an icon (True = check, False = cross, None = amber dot) sliding in one by one.
    items: list of (text, ok)."""
    for i, (s, ok) in enumerate(items):
        p = ease(seg(t, t0 + i * gap, t0 + 0.3 + i * gap))
        if p <= 0: continue
        y = y0 + i * step + (1 - p) * 30
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle([70, y - 62, W - 70, y + 62], 36, fill=rgba(NAVY2, p))
        if ok is True: check_icon(ld, 145, y, 36, a=p)
        elif ok is False: cross_icon(ld, 145, y, 36, a=p)
        else: ld.ellipse([125, y - 20, 165, y + 20], fill=rgba(AMBER, p))
        ld.text((210, y), s, font=F("Bold", size), fill=rgba(WHITE, p), anchor="lm")
        base.alpha_composite(lay)

# ---------- navigation (cell cursor jumps, name box) ----------
def lerp_box(b0, b1, p):
    """Interpolate two [x0, y0, x1, y1] boxes (p: 0..1)."""
    return [u + (v - u) * p for u, v in zip(b0, b1)]

def name_box(base, cx, cy, s, a=1.0, size=44, flash=0.0):
    """Drawn 'Name Box' chip showing the active cell address, e.g. "A5000". flash 0..1 tints it amber."""
    f = F("Mono", size)
    w = max(220, f.getlength(s) + 70); h = size * 2.0
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    bg = tuple(int(WHITE[i] + (AMBER[i] - WHITE[i]) * clamp(flash)) for i in range(3))
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 18, fill=rgba(bg, a))
    d.text((cx, cy), s, font=f, fill=rgba(NAVY, a), anchor="mm")
    base.alpha_composite(lay)
