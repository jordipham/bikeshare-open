"""Exercise 4: target transformations for ridge and hgb.

Validation only by default. The test set is touched once, with --test.
Not part of `make all`, so reports/metrics.json stays untransformed.
Run: python -m src.ex4_target        (validation)
     python -m src.ex4_target --test (test, once, at the end)
"""
import sys

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, r2_score

from src.config import PROCESSED, TARGET
from src.features import feature_columns
from src.train import MODELS, temporal_split

TRANSFORMS = {
    "none": (lambda y, d: y, lambda p, d: p),
    "log1p": (lambda y, d: np.log1p(y), lambda p, d: np.expm1(p)),
    "diff_lag1": (lambda y, d: y - d["cnt_lag_1"], lambda p, d: p + d["cnt_lag_1"].to_numpy()),
}


def main(split: str) -> None:
    df = pd.read_parquet(PROCESSED)
    train, valid, test = temporal_split(df)
    ev = {"valid": valid, "test": test}[split]
    cols = feature_columns(df)
    for tname, (fwd, inv) in TRANSFORMS.items():
        for name in ("ridge", "hgb"):
            model = clone(MODELS[name]).fit(train[cols], fwd(train[TARGET], train))
            pred = inv(model.predict(ev[cols]), ev)
            r2 = r2_score(ev[TARGET], pred)
            mae = mean_absolute_error(ev[TARGET], pred)
            print(f"{split:5s} {tname:9s} {name:5s} r2={r2:.4f} mae={mae:.1f}")


if __name__ == "__main__":
    main("test" if "--test" in sys.argv else "valid")
