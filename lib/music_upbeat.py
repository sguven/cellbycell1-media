"""Original upbeat background music generated in code (no licensed audio).

NOTE (2026-11-10): the house-pop sound below is LEGACY (sounded metallic). New Reels use the clean styles of
lib/music_clean.py via music_styles.pick_style(slug) -> make_track(..., style=style, seed=seed).

make_track(duration, cuts, impacts, out_wav): 118-128 BPM four-on-the-floor house-pop loop,
claps on 2 and 4, offbeat hats, bouncy bass, bright pluck hook, whoosh into each cut,
impact hits on reveals, fade-out of the last 1.5 s, normalized to about -15 LUFS / <= -1.5 dBTP.
"""
import numpy as np
from scipy.signal import butter, sosfilt
import pyloudnorm as pyln
import wave

SR = 44100

def _env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    att = np.clip(t / a, 0, 1)
    return att * np.exp(-t / d)

def _noise(n, rng): return rng.uniform(-1, 1, n)

def _bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos"); return sosfilt(sos, x)

def _hp(x, f, order=2):
    sos = butter(order, f, btype="high", fs=SR, output="sos"); return sosfilt(sos, x)

def _lp(x, f, order=2):
    sos = butter(order, f, btype="low", fs=SR, output="sos"); return sosfilt(sos, x)

def kick(rng):
    n = int(0.32 * SR); t = np.arange(n) / SR
    f = 52 + 110 * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    click = _hp(_noise(n, rng), 3000) * np.exp(-t / 0.004) * 0.3
    return (np.sin(ph) * np.exp(-t / 0.16) + click) * 0.95

def clap(rng):
    n = int(0.25 * SR); t = np.arange(n) / SR
    x = _bp(_noise(n, rng), 900, 4500)
    env = np.exp(-t / 0.06)
    for k in (0.0, 0.011, 0.022):
        i = int(k * SR); env[i:i + 300] += 0.6
    return x * env * 0.55

def hat(rng, open_=False):
    n = int((0.18 if open_ else 0.05) * SR); t = np.arange(n) / SR
    return _hp(_noise(n, rng), 7000) * np.exp(-t / (0.06 if open_ else 0.015)) * 0.35

def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

def saw(freq, n, detune=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for dt in ((-detune, 0, detune) if detune else (0,)):
        f = freq * (1 + dt)
        out += 2 * ((t * f) % 1.0) - 1
    return out / (3 if detune else 1)

def pluck(freq, n):
    x = saw(freq, n, detune=0.006) * _env(n, 0.002, 0.12)
    x += np.sin(2 * np.pi * freq * 2 * np.arange(n) / SR) * _env(n, 0.001, 0.05) * 0.3
    return _lp(x, 5200)

def bass_note(freq, n):
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * freq * t) * 0.8 + saw(freq, n) * 0.35
    return _lp(x, 900) * _env(n, 0.004, 0.14)

def whoosh(rng, dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    x = _noise(n, rng)
    out = np.zeros(n)
    steps = 12
    for k in range(steps):
        a, b = int(k * n / steps), int((k + 1) * n / steps)
        lo = 400 + 5000 * (k / steps) ** 2
        out[a:b] = _bp(x, lo, min(lo * 2.2, 18000))[a:b]
    env = (t / dur) ** 2
    return out * env * 0.5

def impact(rng):
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 38 + 80 * np.exp(-t / 0.06)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.35)
    crash = _hp(_noise(n, rng), 2500) * np.exp(-t / 0.25) * 0.35
    return boom * 0.9 + crash

def _add(buf, x, start):
    i = int(start * SR)
    if i >= len(buf) or i + len(x) <= 0: return
    j = min(len(buf), i + len(x))
    buf[max(0, i):j] += x[max(0, -i):j - i]

def make_track(duration, cuts=(), impacts=(), out_wav="music.wav", bpm=124, seed=11,
               prog=((57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)), lufs=-15.0, style=None):
    """Use music_styles.pick_style(slug) and pass style=... (clean styles, see lib/music_clean.py).
    style=None -> a clean style chosen from the seed (NOT the old metallic house-pop sound).
    style="housepop" (legacy) and the other legacy names only exist to re-render old Reels. Returns integrated LUFS."""
    if style is None:
        try: from . import music_clean
        except ImportError: import music_clean
        st = music_clean.CLEAN_STYLES[int(seed) % len(music_clean.CLEAN_STYLES)]
        return music_clean.make_clean(duration, cuts, impacts, out_wav, style=st, seed=seed, lufs=lufs)
    if style != "housepop":
        try: from . import music_styles
        except ImportError: import music_styles
        return music_styles.make_styled(duration, cuts, impacts, out_wav, style=style, seed=seed, lufs=lufs)
    rng = np.random.default_rng(seed)
    n = int(duration * SR) + SR
    drums = np.zeros(n); bass = np.zeros(n); synth = np.zeros(n); fx = np.zeros(n)
    beat = 60.0 / bpm
    K, C = kick(rng), clap(rng)
    nbeats = int(duration / beat) + 2
    for b in range(nbeats):
        t0 = b * beat
        _add(drums, K, t0)
        if b % 4 in (1, 3): _add(drums, C, t0)
        _add(drums, hat(rng, open_=(b % 2 == 1)), t0 + beat / 2)
        _add(drums, hat(rng) * 0.6, t0 + beat * 0.25)
        _add(drums, hat(rng) * 0.6, t0 + beat * 0.75)
        bar = (b // 4) % len(prog)
        chord = prog[bar]
        root = midi(chord[0] - 24)
        # bouncy offbeat bass + octave pop
        _add(bass, bass_note(root, int(beat * 0.45 * SR)), t0 + beat / 2)
        if b % 2 == 1: _add(bass, bass_note(root * 2, int(beat * 0.2 * SR)) * 0.5, t0 + beat * 0.75)
        # pluck hook: arpeggio in 16ths with a rhythmic pattern
        pat = [1, 0, 1, 1, 0, 1, 0, 1]
        notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 24]
        for s in range(2):
            idx = (b % 4) * 2 + s
            if pat[idx]:
                m = notes[(idx + bar) % 4]
                _add(synth, pluck(midi(m), int(beat * 0.5 * SR)) * 0.5, t0 + s * beat / 2)
        # chord stab on beat 1 of each bar
        if b % 4 == 0:
            st = sum(saw(midi(m), int(beat * 0.6 * SR), 0.008) for m in chord) / 3
            st = _lp(st, 3000) * _env(len(st), 0.003, 0.18) * 0.35
            _add(synth, st, t0)
    for c in cuts:
        w = whoosh(rng); _add(fx, w, c - len(w) / SR)
    for im in impacts:
        _add(fx, impact(rng), im)
    # sidechain-ish pump on synth and bass from the kick
    tt = np.arange(n) / SR
    pump = 1 - 0.45 * np.exp(-((tt % beat) / 0.09))
    mix = drums * 0.9 + bass * 0.75 * pump + synth * 0.7 * pump + fx * 0.8
    mix = mix[:int(duration * SR)]
    # fade out last 1.5 s
    fo = int(1.5 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    # stereo: slight width on synth via delay
    L = mix.copy(); R = mix.copy()
    d = int(0.012 * SR)
    sy = (synth * 0.7 * pump)[:len(mix)]
    R[d:] += sy[:-d] * 0.25; L += sy * 0.05
    st = np.stack([L, R], axis=1)
    meter = pyln.Meter(SR)
    st = pyln.normalize.loudness(st, meter.integrated_loudness(st), lufs)
    # soft limiter to keep peaks under -1.5 dBFS (with oversampling margin)
    ceil = 10 ** (-2.0 / 20)
    st = np.tanh(st / ceil) * ceil
    st = pyln.normalize.loudness(st, meter.integrated_loudness(st), lufs)
    st = np.clip(st, -ceil, ceil)
    pcm = (st * 32767).astype(np.int16)
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return meter.integrated_loudness(st)
