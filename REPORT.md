# Bikeshare demand: agentic programming report

Daily Capital Bikeshare ridership, 2011-2012. Train = 2011, valid = H1 2012,
test = H2 2012 (`src.train.temporal_split`). All numbers below are from
`reports/metrics.json` (produced by `make all`) unless stated otherwise.

## Results

Before = the starter pipeline (14 features). After = with my feature
`hum_cnt_lag_1` (15 features), the committed `reports/metrics.json`.

| Model | Split | R^2 before | MAE before | R^2 after | MAE after |
|---|---|---|---|---|---|
| baseline_mean | valid | -0.9318 | 2002.2 | -0.9318 | 2002.2 |
| baseline_mean | test | -2.1441 | 2847.7 | -2.1441 | 2847.7 |
| baseline_persistence | valid | 0.4507 | 900.6 | 0.4507 | 900.6 |
| baseline_persistence | test | 0.5099 | 840.1 | 0.5099 | 840.1 |
| ridge | valid | 0.6475 | 832.9 | 0.6853 | 770.9 |
| ridge | test | 0.5833 | 947.1 | 0.5997 | 916.4 |
| hgb | valid | 0.2185 | 1296.6 | 0.1343 | 1351.5 |
| hgb | test | -0.4975 | 1972.6 | -0.8198 | 2173.5 |

The feature was chosen and kept on validation only (ridge +0.038 R^2, above
the 0.01 noise threshold for a 182-day split). It hurt hgb (-0.084). The test
rows were produced by `make all` and played no part in the decision.

## Headline Finding

The best model, ridge (test R^2 0.600), beats yesterday's count (persistence, 0.510) on R^2, but it loses on MAE (916 compared to 840 rides per day). Furthermore, gradient boosting fails outright on test with an R^2 of -0.82. This is due to extrapolation: ridership rose from an average of 3494 rides per day in 2011 to 6043 in H2 2012, the max in 2011 is 6043, and 57% (computed on the 714-row feature table; the assignment page does cite 56%) of the test days exceeded it. Essentially, a tree cannot predict above the largest target that it saw in training, whereas a linear model can.

The methodological finding is that the agent repeatedly made plausible but invalid work, and these problems were caught by checks I ran myself: at times, the agent tried to overwrite the raw data, invented column names, hard-coded the mean baseline's R^2 to minus infinity, added placeholder models to make tests pass, wrote a test that compared my feature to itself, and cited a `CLAUDE.md` line that just didn't exist. When exploring seeding faults, there was also a blind spot in the suite: when removing the calendar reindex, all the tests went green (`docs/SEEDED_FAULTS.md`).

## Exercise 4: Exploring a target transformation for gradient boosting

`src/ex4_target.py` refits ridge and hgb on transformed targets. It is not
part of `make all`, so `reports/metrics.json` stays untransformed. I tuned on
validation only and committed that choice before touching the test set once
(`python -m src.ex4_target --test`, saved in `reports/ex4_test_once.txt`).

| Target | ridge valid | hgb valid | ridge test | hgb test |
|---|---|---|---|---|
| none | 0.6853 | 0.1343 | 0.5997 | -0.8198 |
| log1p | 0.1169 | 0.0527 | -0.6964 | -0.8698 |
| diff_lag1 (cnt - cnt_lag_1) | 0.6896 | 0.4875 | 0.6033 | 0.2741 |

`log1p` does not help: 2012's log counts still exceed anything in 2011, so
trees still cannot reach them. Predicting the day-over-day change
(`diff_lag1`) and adding yesterday back works on the actual mechanism: trees
only have to learn changes, whose range is similar in both years, while the
level comes from `cnt_lag_1`. It lifted hgb from -0.82 to +0.27 on test.

**Is it defensible?** Yes, as a fix: it targets the extrapolation failure,
uses only `cnt_lag_1` (known at prediction time) and is exactly invertible.
But it does not make gradient boosting competitive. It turns hgb into
"persistence plus a tree correction", which still trails persistence itself
on test (0.27 vs 0.51) and ridge (0.60), and part of its validation gain
(0.49) did not carry over. I would not report it as gradient boosting
"winning".

## Exercise 5: Ridge vs. Persistence

On test, ridge beats persistence by 0.09 R^2 (0.600 vs 0.510; 0.07 for the
starter's ridge) but is worse on MAE by 76 rides/day (916 vs 840). The
standardised ridge coefficients (starter feature set, fitted on 2011) show it
is not just "yesterday again": recent demand dominates (`cnt_roll_7` +567,
`cnt_lag_1` +362) but weather adds signal of similar total size
(`weather_severity` -280, `temp` +200, `windspeed` -156, `hum` -117), which
persistence cannot have. R^2 weights large misses heavily, so ridge's gain
comes from big weather-driven swings, while persistence is closer on an
ordinary day. For a daily operations use where the typical error matters
most, I would not deploy ridge over persistence yet: a 0.09 R^2 gain from one
182-day test window does not outweigh being 76 rides/day worse on a typical
day. I would deploy ridge only if the cost of large misses (storms, holidays)
dominates.

## Attribution

**Model:** `bikeshare-coder` = `qwen3.5:9b` with a 64k context, run locally
through Ollama 0.40.16 and Claude Code 2.1.326. I did not switch models.

**Agent-generated (bikeshare-coder):**
- The `hum_cnt_lag_1` implementation in `src/features.py` (via `/new-feature`).
- Fixes for seeded faults 1-3 (3, 5 and 4 turns); for faults 2 and 3 I
  replaced its fix with the project's standard form.
- The Step 2 data characterisation, Step 6 explanations, and the
  `agent/audit.py` run in `reports/audit.jsonl`, all checked against my own
  pandas output.

**My decisions** (each has a line in `docs/DECISIONS.md`):
- Keep the denylist and add a contract test that every raw column is
  classified (`RAW_INPUT_COLS`).
- Replace the agent's self-comparing test with a hand-computed value on
  2011-06-15 (230692.3297), committed failing before the feature.
- Keep `hum_cnt_lag_1` on the validation result only.
- Choose the three seeded faults, and the unseen Bash `cp` fault; implement a
  SHA-256 guard on the raw file and make it read-only.
- Reject the agent's edits to tests and its rewrites of `src/train.py` and
  `src/leakage_demo.py`; restore the starter's versions.
- Choose `diff_lag1` on validation and touch the test set once.
- Update `CLAUDE.md` with rules drawn from the agent's actual mistakes.
- Write the `/ablation` skill.

**Other AI Assistance** Claude (chat) served as assistance on the side. It helped with determining 
courses of action when command lines in terminal broke, when commands in Claude Code were stalling, 
and when writing reports and other prose to ensure the direction and content was accurate along with
different blocks of code for efficiency.
