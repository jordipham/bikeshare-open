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
- 2026-11-17: Fix fault 3: restore `WEATHER_ORDER` to GOOD/MISTY/BAD. Agent fixed it in 4 turns but left a dead `STORM` label and cited a non-existent CLAUDE.md line; I restored the original.
- 2026-11-17: Fault 4 (unseen): a Bash `cp` into `data/raw/` bypasses the Edit|Write hook and all 15 tests. Implemented `test_raw_data_unchanged` (SHA-256 of the raw file) in `tests/test_contract.py`, and made the file read-only locally. Also recorded that removing `reindex_to_calendar` is not caught by the suite.
- 2026-11-18: Ran `agent/audit.py` on my repo (bikeshare-coder): verdict leakage none, temporal ok, baselines reported, reproducible. Its 3 findings change no number and are weak or wrong (DummyRegressor has no random_state; speculative hgb nondeterminism; the features print already uses feature_columns). Stopped ignoring `reports/` so `audit.jsonl` and `metrics.json` are committed.
- 2026-11-18: Exercise 4: added `src/ex4_target.py` (not in `make all`; `metrics.json` stays untransformed). Validation only: diff_lag1 (predict cnt - cnt_lag_1, add back) lifts hgb R^2 0.1343 -> 0.4875 (ridge 0.6853 -> 0.6896); log1p hurts both. Chose diff_lag1 on validation; defensible (targets the tree extrapolation limit, uses only cnt_lag_1, exactly invertible) but makes hgb persistence plus a correction. Test not yet touched.
- 2026-11-18: Exercise 4: touched the test set once (`python -m src.ex4_target --test`, saved to reports/ex4_test_once.txt). diff_lag1 hgb test R^2 -0.8198 -> 0.2741, still below persistence (0.5099) and ridge (0.6033). Verdict: defensible fix for the extrapolation failure, but it does not make hgb competitive.
- 2026-11-18: Added `RAW_INPUT_COLS` to `src/config.py` and `test_every_raw_column_is_classified` to `tests/test_contract.py`: every raw column except `dteday` must be in exactly one of LEAKAGE / TIME_INDEX / UNVERIFIED / RAW_INPUT. Shown red first (`unclassified raw columns: [hum]`) with `hum` left out, then green. Implements the safeguard from the Step 4 denylist decision.
- 2026-11-18: Added my skill `.claude/skills/ablation/SKILL.md` (takes `$ARGUMENTS`; validation-only, read-only) backed by `src/ablate.py`. Invoked `/ablation hum_cnt_lag_1`: agent ran the script and quoted ridge +0.0378 / hgb -0.0842 correctly, but skipped step 5 (suggest a DECISIONS line).
- 2026-11-18: Updated `CLAUDE.md` (39 lines). Removed the Commands list (derivable from the Makefile; `make data` invited the Step 2 overwrite attempt). Added rules from observed agent errors: never touch data/raw by any tool (Fault 4), fix code not tests (agent tried to edit my test and added placeholder MODELS), do not re-implement the split, no test-set runs while iterating, read the CSV header first (invented column names), classify every raw column.
- 2026-11-18: Wrote REPORT.md (Results, Headline finding, Exercise 4, Exercise 5, Attribution).
