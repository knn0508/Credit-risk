"""Experiment protokolu (decisions/0001): stratified 80/20 train/holdout + train daxilində 5-fold CV. Seed configs/training.yaml-dan."""
import json
from pathlib import Path

import numpy as np
import yaml
from sklearn.model_selection import StratifiedKFold, train_test_split

DEFAULT_CONFIG = "configs/training.yaml"


def load_config(path: str = DEFAULT_CONFIG) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def make_split(ids, y, seed: int, holdout_size: float = 0.2) -> dict:
    """Holdout yalnız son hesabat üçündür; tuning/hədd seçimində istifadə olunmur."""
    ids, y = np.asarray(ids), np.asarray(y)
    tr, ho = train_test_split(ids, test_size=holdout_size, stratify=y, random_state=seed)
    return {"seed": seed, "holdout_size": holdout_size,
            "train_ids": sorted(int(i) for i in tr), "holdout_ids": sorted(int(i) for i in ho)}


def save_split(split: dict, path) -> None:
    Path(path).write_text(json.dumps(split), encoding="utf-8")


def cv_folds(y, seed: int, n_splits: int):
    """Yield (fold, train_idx, valid_idx) — mövqe indeksləri."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for k, (a, b) in enumerate(skf.split(np.zeros(len(y)), y)):
        yield k, a, b
