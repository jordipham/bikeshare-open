# Bikeshare demand capstone

Daily Capital Bikeshare counts, 2011-2012. We forecast `cnt` (total daily
rides) from calendar, weather, and lagged-demand features.

## Non-negotiable rules
- **Never** put `casual` or `registered` in a feature set:
  `casual + registered == cnt` exactly. Derive feature lists from
  `FORBIDDEN` in `src/config.py`; never hand-type them.
- **Never** split randomly or re-implement the split. Use
  `src.train.temporal_split`: train = 2011, valid = H1 2012, test = H2 2012.
- **Never** evaluate on the test set while iterating. The one test-set run
  (`python -m src.ex4_target --test`) is done; do not rerun it.
- A new lag or rolling feature must be built after
  `src.features.reindex_to_calendar` and must `.shift(1)` before it
  aggregates. Add a named-date, hand-computed test in `tests/test_leakage.py`.
- Every raw column except `dteday` must be in exactly one set in
  `src/config.py` (LEAKAGE / TIME_INDEX / UNVERIFIED / RAW_INPUT).
- Report the mean **and** persistence baselines with every model. A negative
  R^2 is a finding, not a bug to hide.

## Never touch
- `data/raw/bike_daily.csv`: never download, copy, or write over it, with any
  tool including Bash. `tests/test_contract.py` checks its SHA-256.
- Tests: when `make test` fails, fix the code, not the test or its expected
  values. Ask before editing anything in `tests/`.

## Working style
- Run `make test` after every change and before claiming anything works.
- Read the CSV header before writing code: the date column is `dteday`.
- Standard library, pandas, scikit-learn only; versions are pinned.
- Paths and constants live in `src/config.py`. Nothing is hardcoded twice.

## Gotchas
- The mirror is missing 2011-03-10: 728 rows from 2011-01-03, not 731.
- `weather` uses the labels `GOOD` / `MISTY` / `BAD`, not the UCI codes 1-4.
- Ridership grew ~65% from 2011 to 2012, so tree models trained on 2011
  cannot extrapolate to 2012. That is the headline result, not an error.
- 2012-10-29 (Hurricane Sandy, 22 rides) is in the test set.
