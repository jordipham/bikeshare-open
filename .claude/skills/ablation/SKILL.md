---
name: ablation
description: Measure what a feature contributes by dropping it and refitting on the validation set. Use when asked whether a feature matters, or to ablate, drop or remove a feature.
allowed-tools: Read, Bash(python -m src.ablate*), Bash(make features*)
---

# Ablation: $ARGUMENTS

Work in this order. Do not edit any file.

1. **Run the ablation.** If `data/processed/features.parquet` is missing, run
   `make features` first. Then run exactly `python -m src.ablate $ARGUMENTS`.
   If it reports an unknown feature, show the available list and stop.

2. **Report only the printed numbers.** For ridge and hgb, quote the
   validation R^2 with and without the feature and the delta. Do not compute
   or estimate numbers yourself.

3. **Judge the size.** A delta under 0.01 is inside the noise of a single
   182-day validation split: say so plainly and call the feature removable.

4. **Never touch the test set** and never run `make train` or `src.train`;
   ablation is validation-only.

5. **Suggest, do not write,** one `docs/DECISIONS.md` line: the date, the
   feature, both deltas, and keep or drop.
