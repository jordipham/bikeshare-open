# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

- 2026-11-17: Step 2 plan-mode check of the agent (bikeshare-coder, qwen3.5:9b) against pandas. It verified the following information: 728 rows, 2011-01-03 to 2012-12-31, weather GOOD/MISTY/BAD = 463/245/20, 2011-03-10 missing. Some agent errors that occurred include such: missed `casual`/`registered` as the leak; called `cnt_2d_bfr` leakage (it is an unverified lag, `UNVERIFIED_COLS`); justified excluding `instant` with "hour-specific patterns" in daily data; claimed `mnth` skips months (all 12 present); invented column names (`date`, `cnt_registered`, `cnt_casual`); tried to overwrite `data/raw/bike_daily.csv` and, when blocked, asked me to run the download myself with `!`.

- 2026-11-17: Keep a denylist (`FORBIDDEN`) over an allowlist. This means I accept the failure that a new raw column can enter features silently, but in the end, it will be handled by `tests/test_contract.py` (will be made later) which flags any column not classified in `src/config.py`.

- 2026-11-17: Add `hum_cnt_lag_1` = same-day `hum` x `cnt_lag_1` via /new-feature. What was available at prediction time: today's weather and yesterday's count. Validation R^2 ridge 0.6475 -> 0.6853 (+0.038), hgb 0.2185 -> 0.1343 (-0.084). Kept (ridge gain > 0.01); hgb worsens because trees cannot extrapolate the interaction. Replaced the agent's tautological test with a hand-computed value on 2011-06-15.
- 2026-11-17: Seed fault 1 (Exercise 2): `cnt_lag_1` uses `shift(0)` (today's count). Leakage tests turn red (3 failed) and the hook exits 2.
- 2026-11-17: Fix fault 1: restore `cnt_lag_1` to `shift(1)`. Agent took 3 turns; tests green (15 passed).
- 2026-11-17: Seed fault 2 (Exercise 2): break a lag feature in `src/features.py` (details in docs/SEEDED_FAULTS.md). Leakage tests turn red (1 failed) and the hook exits 2.
- 2026-11-17: Fix fault 2: restore `.shift(1)` before the 7-day rolling mean. Agent fixed it in 5 turns with `closed="left"` (equivalent values) but I kept `.shift(1)` per the CLAUDE.md rule.
- 2026-11-17: Seed fault 3 (Exercise 2): break the weather encoding in `src/features.py` (details in docs/SEEDED_FAULTS.md). Tests error (13) and the hook exits 2.
