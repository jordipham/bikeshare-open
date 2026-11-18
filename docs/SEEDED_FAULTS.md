# Seeded faults

## Fault 1: `cnt_lag_1` uses today's count

**Change** (`src/features.py`):
```diff
-    out["cnt_lag_1"] = out[TARGET].shift(1)
+    out["cnt_lag_1"] = out[TARGET].shift(0)
```

**`make test` (red):**
```
FAILED tests/test_leakage.py::test_lags_are_true_calendar_lags - AssertionErr...
FAILED tests/test_leakage.py::test_lag_is_not_the_target - assert not np.True_
FAILED tests/test_leakage.py::test_hum_cnt_lag_1_on_named_date - assert np.fl...
3 failed, 12 passed in 1.60s
```

**Hook stderr (exit 2):**
```
Leakage tests failed after editing src/features.py:
E       assert np.float64(244323.506) == 230692.3297 ± 0.230692
FAILED tests/test_leakage.py::test_lags_are_true_calendar_lags - AssertionErr...
FAILED tests/test_leakage.py::test_lag_is_not_the_target - assert not np.True_
FAILED tests/test_leakage.py::test_hum_cnt_lag_1_on_named_date - assert np.fl...
3 failed, 5 passed in 0.30s
exit=2
```

**Agent turns to fix:** 3 (ran `make test`, read `src/features.py`, edited line 74 back to `shift(1)`). It found the bug partly from the seed commit message, did not re-run `make test` to verify, and then tried to change the named-date test expectation (stopped).

## Fault 2: 7-day rolling mean includes today

**Change** (`src/features.py`):
```diff
-    out["cnt_roll_7"] = out[TARGET].shift(1).rolling(LAG_WARMUP).mean()
+    out["cnt_roll_7"] = out[TARGET].rolling(LAG_WARMUP).mean()
```

**`make test` (red):**
```
E             comparison failed
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 14 passed in 1.65s
```

**Hook stderr (exit 2):**
```

tests/test_leakage.py:57: AssertionError
=========================== short test summary info ============================
FAILED tests/test_leakage.py::test_rolling_mean_excludes_today - assert np.fl...
1 failed, 7 passed in 0.28s
exit=2
```

**Agent turns to fix:** 5 (ran `make test`, read `src/features.py` and `src/config.py`, edited, re-ran `make test`: 15 passed). Its fix used `rolling(LAG_WARMUP, closed="left")`: same values (ridge valid R^2 0.6853) but breaks the CLAUDE.md rule to `.shift(1)` before aggregating, so I restored `.shift(1).rolling(...)`.

## Fault 3: weather label renamed (BAD -> STORM)

**Change** (`src/features.py`):
```diff
-WEATHER_ORDER = {"GOOD": 0, "MISTY": 1, "BAD": 2}
+WEATHER_ORDER = {"GOOD": 0, "MISTY": 1, "STORM": 2}
```

**`make test` (red):**
```
E           ValueError: unmapped weather labels: ['BAD']
ERROR tests/test_split.py::test_no_overlapping_dates - ValueError: unmapped w...
2 passed, 13 errors in 1.61s
```

**Hook stderr (exit 2):**
```
8 errors in 0.29s
exit=2
```

**Agent turns to fix:** 4 (ran `make test`, read `src/features.py`, edited line 16, re-ran `make test`: 15 passed). Its fix added `"BAD": 2` but kept a dead `"STORM": 3` label, and its summary quoted a CLAUDE.md line that does not exist. I restored the original mapping.

## Fault 4 (unseen by the hook): Bash `cp` into `data/raw/`

**Change:** overwrite the raw data with a copy missing its last row, as an agent re-downloading or copying data might:
```
cp /tmp/raw_bad.csv data/raw/bike_daily.csv
```

**What happened:** the hook stayed silent (`hook exit=0`; in real use it does not run at all, because `.claude/settings.json` only triggers it for Edit|Write), and the permission deny rules do not cover Bash. All tests still passed with a day of data missing:
```
15 passed in 1.60s
```
Only the file hash (`0c437d8d...` instead of `a6bed157...`) and `git status` (` M data/raw/bike_daily.csv`) revealed it.

**What catches it (implemented):**
1. `tests/test_contract.py::test_raw_data_unchanged` asserts the raw file's SHA-256. With the bad copy in place:
```
FAILED tests/test_contract.py::test_raw_data_unchanged - AssertionError: raw ...
1 failed, 15 passed in 1.56s
```
2. `chmod a-w data/raw/bike_daily.csv` makes the file read-only, so a plain `cp` onto it fails with "Permission denied" before anything changes.

## Additional finding: a fault the suite missed

Removing the `reindex_to_calendar(...)` call in `build_features` (the Step 5 calendar-gap bug) left all 15 tests green and the hook at `exit=0`. `test_lags_are_true_calendar_lags` only checks days whose previous calendar day exists in the raw data, so it skips 2011-03-11, the one row the bug breaks. The test is named for this bug but cannot detect it.
