"""Ablation: refit ridge and hgb without the named features; validation only.

Run: python -m src.ablate FEATURE [FEATURE ...]
"""
import sys

import pandas as pd
from sklearn.base import clone
from sklearn.metrics import r2_score

from src.config import PROCESSED, TARGET
from src.features import feature_columns
from src.train import MODELS, temporal_split


def main(drop: list[str]) -> None:
    df = pd.read_parquet(PROCESSED)
    train, valid, _ = temporal_split(df)
    cols = feature_columns(df)
    unknown = [c for c in drop if c not in cols]
    if not drop or unknown:
        sys.exit(f"unknown or missing feature(s): {unknown or drop}; available: {', '.join(cols)}")
    kept = [c for c in cols if c not in drop]
    for name in ("ridge", "hgb"):
        full = clone(MODELS[name]).fit(train[cols], train[TARGET])
        less = clone(MODELS[name]).fit(train[kept], train[TARGET])
        r_full = r2_score(valid[TARGET], full.predict(valid[cols]))
        r_less = r2_score(valid[TARGET], less.predict(valid[kept]))
        print(f"{name:5s} valid R^2 with={r_full:.4f} without={r_less:.4f} delta={r_full - r_less:+.4f}")


if __name__ == "__main__":
    main(sys.argv[1:])
