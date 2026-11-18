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
