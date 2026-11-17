# Decisions

One line per methodological decision: what you chose, why, and what it changed.
Agents append here via the `/new-feature` skill; you append here by hand.

- Exclude `casual`, `registered`: they sum to `cnt` exactly. Leaky model R^2 1.000 -> honest ridge 0.583.
- Exclude `cnt_2d_bfr`: a shipped 2-day lag we cannot test the alignment of. Build our own lags instead.
- Exclude `instant`, `yr`, `days_since_2011`: time indexes let a tree predict a flat constant past 2011 and a linear model extrapolate a trend we have no grounds for.
- Split 2011 / H1 2012 / H2 2012 by date. Test set touched once, after all feature work.
- Report mean and persistence baselines with every score. Persistence (test R^2 0.510, MAE 840) is within 0.07 R^2 of ridge and beats it on MAE; that caveat goes in the report.

- 2026-11-17: Step 2 plan-mode check of the agent (bikeshare-coder, qwen3.5:9b) against pandas. Verified: 728 rows, 2011-01-03 to 2012-12-31, weather GOOD/MISTY/BAD = 463/245/20, 2011-03-10 missing. Agent errors: missed `casual`/`registered` as the leak; called `cnt_2d_bfr` leakage (it is an unverified lag, `UNVERIFIED_COLS`); justified excluding `instant` with "hour-specific patterns" in daily data; claimed `mnth` skips months (all 12 present); invented column names (`date`, `cnt_registered`, `cnt_casual`); tried to overwrite `data/raw/bike_daily.csv` and, when blocked, asked me to run the download myself with `!`.
