# @cellbycell1 performance log

Weekly review of the Reels (data: Windsor.ai, Instagram account 17841476311300072).
Baseline (2026-11-15 analysis): avg ~114 views, ~89% skip rate in the first 3 s, ~2.5 s avg watch time, 17 followers, 0 comments.

## 2026-11-22 (week of 2026-11-15 → 2026-11-21)

Data pulled 2026-11-22 ~17:05 ET from Windsor's cache (no on-demand refresh on this plan), so the last 1–2 days can still grow.
7 Reels counted (11-15 → 11-21). Today's Reel (split-full-names) was posted minutes before the pull and is left out (0 views).

| Date | Slug | Type | Views | Reach | Skip | Avg watch | Likes | Saves | Shares | Comments |
|---|---|---|---|---|---|---|---|---|---|---|
| 11-15 | textjoin-combine | formula | 128 | 114 | 91.5% | 1.79 s | 0 | 0 | 0 | 0 |
| 11-16 | f4-absolute-refs | shortcut | 122 | 108 | 86.7% | 2.42 s | 0 | 0 | 0 | 0 |
| 11-17 | countifs-basics | formula | 129 | 113 | 85.7% | 2.12 s | 2 | 1 | 1 | 0 |
| 11-18 | dropdown-list | visual | 153 | 130 | 85.8% | 4.12 s | 2 | 2 | 0 | 0 |
| 11-19 | sort-function-trap | formula (Excel vs Sheets trap) | 116 | 92 | 92.2% | 1.57 s | 2 | 1 | 0 | 0 |
| 11-20 | paste-values | shortcut | 151 | 132 | 82.3% | 3.48 s | 0 | 3 | 0 | 0 |
| 11-21 | count-unique | formula | 129 | 116 | 84.0% | 2.22 s | 0 | 0 | 0 | 0 |

**Totals / averages:** avg 132.6 views (baseline ~114, +16%), avg reach 115, avg skip 86.9% (baseline ~89%, −2 pts),
avg watch 2.53 s (baseline ~2.5 s, flat), 6 likes, 7 saves, 1 share, **0 comments** (still zero).
Followers: 18 (baseline 17, +1).

**By type:** visual (1) 153 views / 85.8% skip / 4.1 s / 2 saves · shortcut (2) 136.5 / 84.5% / 2.95 s / 3 saves ·
formula (3) 128.7 / 87.1% / 2.04 s / 1 save · Excel-vs-Sheets trap (1) 116 / 92.2% / 1.57 s / 1 save.
No "contrarian" (X → Y) and no "wow" (AI/automation) topic ran this week; the calendar still had the old mix.

**Best 2:** paste-values (lowest skip 82.3%, 3 saves, hook = a broken result "every cell broke") and
dropdown-list (most views 153, longest watch 4.1 s, hook = "10-SECOND DROPDOWN" + visible UI result).
**Worst 2:** sort-function-trap (92.2% skip, 1.6 s; the hook was about argument spelling, a syntax difference) and
textjoin-combine (91.5% skip, 1.8 s, 0 interactions; plain formula topic with a "Stop..." hook).

**What worked:** showing a visible UI/result change (dropdown appearing, pasted cells breaking) and a time promise.
Shortcut and visual topics kept viewers ~1–2 s longer than formula topics.
**What didn't:** formula-syntax topics (TEXTJOIN, SORT arguments, COUNTIFS, UNIQUE) all sat at 1.6–2.2 s watch time;
the Excel-vs-Sheets syntax angle was the weakest hook of the week. Caption questions produced no comments.

### Önümüzdeki hafta için kurallar
1. **Hook:** first frame = a visible broken→fixed result or a UI change (cells breaking, a dropdown/heatmap appearing), with a
   number/time promise or a question in ≤ 2 short lines; never open on an argument/syntax difference. "Stop..." max 1× this week.
2. **Topic mix (2026-11-23 → 11-29):** at most 1 pure-syntax formula (pick NETWORKDAYS *or* INDEX MATCH *or* IF+AND, not more);
   reframe the others as "common mistake" (e.g. percent-change: old/new vs (new−old)/old) or swap them for a "wow" topic
   (AI/automation in Sheets or Excel, verified with WebSearch). Keep at least 2 visual/shortcut topics (sparklines, freeze header, heatmap).
3. **Length & comments:** 15–18 s total, scenes ≤ 2.4 s; end the video (outro) and the caption with the same either/or question
   ("Flash Fill or formula? 👇") so the comment prompt is seen, not only read.


## 2026-11-26: opening-format test started (owner's request)
State before the test (Windsor, 2026-11-26): 26 followers, 24 posts; Reels since 11-15 sit at ~115–155 views, 82–92% skip,
1.6–4.1 s watch, 0 comments. From 2026-11-27 each Reel uses the `opening` set in `content/calendar.csv`
(`cold_open`, `quiz_open`, `chat_open`; see STYLE.md "Opening formats"). All posts up to 11-26 are `headline`.
**Next weekly review:** add a "By opening" table (n, avg views, avg skip, avg watch, saves, comments) and compare with the
`headline` baseline (avg skip 86.9%, avg watch 2.53 s). Keep any format that is at least 5 points lower on skip over 2+ Reels,
drop one that is worse than `headline`, and fill the next week's `opening` column accordingly.
