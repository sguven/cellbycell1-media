# @cellbycell1 — Reels style guide and daily workflow

Faceless, animated Excel & Google Sheets tips for a US audience, in English.
One Reel per day, posted automatically via the Windsor.ai for Social Media connector
(Instagram account id `17841476311300072`, action `create_video_post`).
Sister account of @cleaneverycorner (same pipeline, different brand).

## Weekly mix
Roughly 3 formula + 2 shortcut/productivity + 1 data-cleaning + 1 visual (formatting, charts, checkboxes) per week.
The plan lives in `content/calendar.csv`; every post is logged in `content/posted.csv`.
When the calendar runs out, add the next 4 weeks of topics (same mix, no repeats of `posted.csv`) and commit them.

## Posting times (US Eastern, from the setup guide; adjust after 2 weeks of Insights)
Mon ~14:30 · Tue–Thu ~13:00 · Fri–Sat ~12:30 · Sun ~17:00

## Video spec
- 1080x1920, 30 fps, H.264 yuv420p (CRF 18, preset veryfast), AAC 192k, 15–25 s (max 25 s; owner's rule from the 2026-11-15 performance review: ~89% of viewers skip in the first 3 s).
- Keep text out of the top 250 px and bottom 350 px (Instagram UI).
- Fonts: Poppins (Bold titles, Medium body); formulas in DejaVu Sans Mono Bold. No emoji drawn in video.
- Brand colors: navy `#13233F` background with a faint grid, panel navy `#26385A`, amber `#FFB020` accent,
  white text. Green `#22B070` = correct, red `#EA484D` = wrong. Range tints: amber = lookup/search range, blue `#58A0FF` = return range.
- Building blocks (all in `lib/engine.py`, extend it, never rewrite per video): `Sheet` (light spreadsheet with
  column letters + row numbers, cell tints and outlines), `formula_bar` (typing animation, colored ranges),
  `result_chip` (green check / red cross), `label_card` (tag pill + title), `pop_text`, `punch`, `shake`, `outro`;
  for data validation / UI steps: `Sheet.draw(dropdowns=...)` (status chips + arrow), `dropdown_list`, `pointer`,
  `panel` + `form_field` (drawn dialogs with typing inputs).
- Structure: hook (≈2–3 s) → problem or "why" → the fix on a real mini table (formula AFTER the result) → optional bonus
  → "Works in" (Excel version + Google Sheets, or flag if one app only) → outro card "Save this for your next spreadsheet!"
  + "Follow @cellbycell1". Every scene ≤ 2–3 s, at most 2 short text blocks on screen at once, constant motion, low text
  density. The last frame crossfades back into the first (`loop_back` in engine.py) so the Reel loops.
- Reference implementation: `reels/2026-11-05-xlookup-vs-vlookup/render.py` (first Reel).
  Each Reel gets its own folder with `render.py`, the mp4, `cover.jpg` and `caption.txt`.

## Opening formats: hook test from 2026-11-27 (owner's request, takes priority over the hook rules below)
Why: with the amber-headline title card ~87% of viewers swipe away in the first 3 s (avg watch ~2.5 s). It reads like an
ad slide: big headline, small table, empty navy. From 2026-11-27 every Reel opens with one of three new formats instead.
**`content/calendar.csv` has an `opening` column: use the format named there for that day.** No value there = rotate
`cold_open` → `quiz_open` → `chat_open`, never the same as either of the last two rows of `content/posted.csv`.

| opening | first frame | best for |
|---|---|---|
| `cold_open` | full-screen sheet on the light canvas, the fix/break already running in frame 3, caption sticker at ~0.35 s | visual, shortcut, data-cleaning topics |
| `quiz_open` | question sticker + sheet + two answer cards (A/B) + countdown, answer lands at ~1.8 s | "common mistake" and formula topics (wrong answer = the real common mistake) |
| `chat_open` | a message from a manager/coworker creates the stakes, the sheet answers it at ~1.2 s | formula topics with a real-life use (IF, lookups, dates) |
| `headline` | the old amber headline card | control only; do not use during the test |

- Helpers are in `lib/hooks.py` (`screen_bg`, `big_sheet`, `sticker`, `chat_bubble`, `typing_dots`, `quiz_cards`, `camera`,
  `shake_bg`). One full worked example of each format: `tools/hook_demo.py` (`python3 tools/hook_demo.py stills <dir>`).
  Copy the matching `sc_*` function into the day's `render.py` as `sc_hook` and adapt data and texts.
- Rules for all three: motion from frame 0 (use `camera`), the sheet covers at least half of the screen with cell text
  ≥ 46 px, ONE short text block in the first second (max 6 words, no formula text), every value computed from the table,
  hook scene 2.2–2.6 s. Quiz answers must be short (a number or 1–2 words); the wrong one is what people really type.
  Chat messages: max 9 words each, no real names or companies.
- After the hook the Reel continues on the usual navy scenes (`background()`), unchanged.
- Cover (`thumb_offset`) = a hook frame where the sticker/question and the result are both visible (≈ 2000 ms).
- Log it: `content/posted.csv` has an `opening` column; write the format used for every post. The weekly review compares
  skip rate and watch time by `opening` against the `headline` baseline and keeps the winner.

## Hook / cover rules
- The first frame must stop the scroll: a huge amber headline of at most 6 words (≥170 px, `fit_font`) + the finished result
  or a bad/good comparison on a clean table. No formula text filling the screen in the first second; the formula comes after
  the result. Rotate hook patterns (question, "Stop...", number/time promise, before/after, "Wait for it");
  "Stop..." at most 2 times per week.
- Show the payoff within the first 1–1.5 s: bad formula crossed out vs good formula with a check, or a before/after table.
- Motion from frame 0: punch-in zoom + quick shake on the headline, pop-in pill like "3 PROBLEMS · 1 FIX" or "10 SECONDS".
- Cover = a hook frame where the headline and the result are fully visible (`thumb_offset` ≈ 2000–2400 ms).

## Music rules
- **Clean, clear sound (owner's request, 2026-11-10):** the old saw/noise-based sounds were too metallic. New Reels use ONLY the
  clean, band-limited styles in `lib/music_clean.py` (piano, marimba, kalimba, glockenspiel, nylon guitar, clean e-piano,
  round sine bass, soft claps/snaps/shaker, light reverb, transparent limiter). Never use `housepop`, `funk`, `disco`,
  `futurebounce`, `dembow`, `trap` or `synthwave` for a new Reel (legacy, kept only to re-render old videos), and do not
  add saw/square leads, white-noise hi-hats or tanh distortion.
- Original, generated in code (no licensed tracks), upbeat and positive, energy from beat 1.
- Whoosh into every scene cut and an impact on the big reveal (pass `cuts` and `impacts` to `make_track`).
- **Style rotation (mandatory for every new Reel):** the sound must differ from video to video. Do not hand-pick style/seed/prog.
  ```python
  import music_styles, music_upbeat   # lib/ is on sys.path in render.py
  style, seed = music_styles.pick_style(slug)          # reads/writes content/music_state.json, idempotent per slug
  music_upbeat.make_track(total, cuts=..., impacts=..., out_wav=wav, style=style, seed=seed)
  ```
  Clean styles: `brightpop` 118 BPM, `pianohouse` 122, `tropical` 104, `acoustic` 112, `keysfunk` 108, `kalimbapop` 96.
  The picker never repeats either of the last two styles and evens out usage; the seed also shifts the key slightly.
  Commit `content/music_state.json` together with the Reel. Presets live in `lib/music_clean.py` (`STYLES` dict); to add a
  style add one entry there and its name to `CLEAN_STYLES` and `music_styles.ROTATION`. Preview: `python3 lib/music_clean.py brightpop 20 /tmp/p.wav`.
- About -15 LUFS integrated, peaks ≤ -1.5 dB (the generator outputs ≤ -2 dB), fade out the last 1.5 s.

## Accuracy rules
- Every formula, shortcut and menu path must be correct. Check against Microsoft Support and Google Docs Editors Help
  before rendering, and compute every result shown on screen from the table (no made-up outputs).
- Say which app/version it works in. Flag differences between Excel and Sheets (e.g. SORT order argument:
  Excel uses 1/-1, Sheets uses TRUE/FALSE; shortcuts that differ on Mac/Windows).
- Mac vs Windows: show Windows keys and mention "Cmd on Mac" when it applies.
- No Microsoft/Google logos or product screenshots; draw the sheet ourselves. No claims of being a real person or an expert.

## Caption
- Short and scannable, max ~900 characters (hard limit 2200). Line 1: hook (a question or the result; don't start with
  "Stop..." every day). Then at most 3 short lines with the formula(s)/keys and what they do, one line on where it works,
  a comment question ("Which do you use: X or Y? 👇" / "What should I cover next? 👇"), then
  "Save this for your next spreadsheet 📌 Follow @cellbycell1 for a daily Excel & Google Sheets trick."
- Exactly 5 hashtags total: `#cellbycell1` + 4 topic tags (base: #exceltips #googlesheets, plus 2 specific like
  #xlookup #spreadsheettips). Never more than 5 (Instagram limit).

## Publishing
1. Commit the final mp4 to `reels/YYYY-MM-DD-<slug>/<slug>.mp4` (+ `cover.jpg`, `caption.txt`) on `main` and push.
2. Check `https://raw.githubusercontent.com/sguven/cellbycell1-media/main/reels/...` returns HTTP 200.
3. Windsor `execute_action` → connector `instagram`, action `create_video_post`, account `17841476311300072`,
   params `video_url`, `caption`, `thumb_offset`, `share_to_feed: true`.
4. Append the post to `content/posted.csv` (date, category, slug, media_id, video_url, opening) and push.
