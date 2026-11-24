"""Build data/processed/{application_train,application_test}.parquet + schema.json (data-contract v1.0).

Usage: python -m src.data.build [--config configs/data.yaml]
Deterministic (no randomness). Train and test go through the identical code path.
"""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.data import aggregate as A
from src.data.inventory import load_config

KEY = "SK_ID_CURR"
TARGET = "TARGET"
SENTINEL_DAYS = A.SENTINEL_DAYS
XNA_COLUMNS = ("CODE_GENDER", "ORGANIZATION_TYPE")


def clean_application(df):
    """Contract item 2. Shared by train, test and (later) inference. Returns lowercase-named frame."""
    df = df.copy()
    df["days_employed_is_anomalous"] = (df.DAYS_EMPLOYED == SENTINEL_DAYS).astype("int8")
    df.loc[df.DAYS_EMPLOYED == SENTINEL_DAYS, "DAYS_EMPLOYED"] = np.nan
    for c in XNA_COLUMNS:
        if c in df.columns:
            df.loc[df[c] == "XNA", c] = np.nan
    df.columns = [c.lower() for c in df.columns]
    return df


def safe_left_join(left, agg, key=KEY.lower()):
    """Left-join an aggregate that is unique on `key`; row count and key uniqueness must not change."""
    assert agg.index.name == key or key in agg.columns, "aggregate must carry the key"
    if key in agg.columns:
        agg = agg.set_index(key)
    assert agg.index.is_unique, f"aggregate not unique on {key} (one-to-many join refused)"
    n = len(left)
    out = left.merge(agg, how="left", left_on=key, right_index=True, validate="many_to_one")
    assert len(out) == n, f"row count changed in join: {n} -> {len(out)}"
    assert out[key].is_unique == left[key].is_unique
    return out


def _lower_key(agg):
    agg = agg.copy()
    agg.index.name = KEY.lower()
    return agg


def add_history_flag(agg, lineage, prefix, count_col):
    """`<prefix>_has_history` for rows present; counts of absent customers become 0 after the join."""
    agg[f"{prefix}_has_history"] = np.int8(1)
    lineage[f"{prefix}_has_history"] = {"source_table": lineage[count_col]["source_table"],
                                        "source_column": KEY, "stat": "has_history"}
    return agg


def fill_after_join(df, lineage):
    """has_history -> 0 and true counts (count/nunique) -> 0 where the customer has no history."""
    for col, l in lineage.items():
        if col not in df.columns:
            continue
        if l["stat"] == "has_history" or (l["stat"] in ("count", "nunique")):
            df[col] = df[col].fillna(0).astype("int32" if l["stat"] != "has_history" else "int8")
    return df


RAW_TABLES = ("application_train", "application_test", "bureau", "bureau_balance", "previous_application",
              "POS_CASH_balance", "credit_card_balance", "installments_payments")


def file_fingerprint(path, chunk=1 << 22):
    """Streaming sha256 + size (large CSVs are never loaded whole)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return {"bytes": Path(path).stat().st_size, "sha256": h.hexdigest()}


def data_version(raw_dir):
    """Per-file fingerprints + one combined id (sha256 over sorted `name:sha256`) -> bundle metadata.data_version."""
    files = {t: file_fingerprint(Path(raw_dir) / f"{t}.csv") for t in RAW_TABLES}
    combined = hashlib.sha256("\n".join(f"{t}:{files[t]['sha256']}" for t in sorted(files)).encode()).hexdigest()
    return {"data_version": combined[:16], "data_sha256": combined, "raw_files": files}


def _git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return None


def build(cfg):
    raw, out_dir = Path(cfg["raw_dir"]), Path(cfg["processed_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    train = clean_application(pd.read_csv(raw / "application_train.csv"))
    test = clean_application(pd.read_csv(raw / "application_test.csv"))
    app_ids = set(train.sk_id_curr) | set(test.sk_id_curr)
    n_train, n_test = len(train), len(test)
    lineage, report = {}, {"rows_before": {"train": n_train, "test": n_test}}

    def attach(agg, lin, prefix, count_col):
        nonlocal train, test, lineage
        agg = _lower_key(agg)
        agg.index = agg.index.astype("int64")
        assert agg.index.isin(list(app_ids)).all(), f"{prefix}: SK_ID_CURR outside application"
        agg = add_history_flag(agg, lin, prefix, count_col)
        lineage.update(lin)
        train = safe_left_join(train, agg)
        test = safe_left_join(test, agg)

    # bureau (+ bureau_balance collapsed to SK_ID_BUREAU first)
    bureau = pd.read_csv(raw / "bureau.csv")
    bb = pd.read_csv(raw / "bureau_balance.csv")
    report["bureau_balance_orphan_rows_dropped"] = int((~bb.SK_ID_BUREAU.isin(bureau.SK_ID_BUREAU)).sum())
    bb = bb[bb.SK_ID_BUREAU.isin(bureau.SK_ID_BUREAU)]
    bb_by_bureau = A.aggregate_bureau_balance(bb)
    del bb
    agg, lin = A.aggregate_bureau(bureau, bb_by_bureau)
    attach(agg, lin, "bureau", "bureau_sk_id_bureau_count")
    del bureau, bb_by_bureau

    agg, lin = A.aggregate_previous_application(pd.read_csv(raw / "previous_application.csv"))
    attach(agg, lin, "previous_application", "previous_application_sk_id_prev_count")
    agg, lin = A.aggregate_pos_cash(pd.read_csv(raw / "POS_CASH_balance.csv"))
    attach(agg, lin, "pos_cash_balance", "pos_cash_balance_sk_id_prev_count")
    agg, lin = A.aggregate_credit_card(pd.read_csv(raw / "credit_card_balance.csv"))
    attach(agg, lin, "credit_card_balance", "credit_card_balance_sk_id_prev_count")
    agg, lin = A.aggregate_installments(pd.read_csv(raw / "installments_payments.csv"))
    attach(agg, lin, "installments_payments", "installments_payments_sk_id_prev_count")

    train, test = fill_after_join(train, lineage), fill_after_join(test, lineage)

    # acceptance gates
    assert len(train) == n_train and len(test) == n_test, "row count changed"
    assert train.sk_id_curr.is_unique and test.sk_id_curr.is_unique
    assert TARGET.lower() in train.columns and TARGET.lower() not in test.columns
    assert list(train.columns.drop(TARGET.lower())) == list(test.columns), "train/test feature mismatch"
    report["rows_after"] = {"train": len(train), "test": len(test)}
    report["n_columns"] = train.shape[1]

    train.to_parquet(out_dir / "application_train.parquet", index=False)
    test.to_parquet(out_dir / "application_test.parquet", index=False)
    report.update(data_version(raw))
    write_schema(train, test, lineage, out_dir / "schema.json", report)
    return train, test


def write_schema(train, test, lineage, path, report):
    cols = []
    for c in train.columns:
        l = lineage.get(c, {"source_table": "application_train/test", "source_column": c.upper(), "stat": None})
        if c == "days_employed_is_anomalous":
            l = {"source_table": "application_train/test", "source_column": "DAYS_EMPLOYED", "stat": "sentinel_flag"}
        if c == TARGET.lower():
            l = {"source_table": "application_train", "source_column": "TARGET", "stat": None}
        cols.append({
            "column": c,
            "dtype": str(train[c].dtype),
            "nullable": bool(train[c].isna().any() or (c in test and test[c].isna().any())),
            "null_pct_train": round(float(train[c].isna().mean() * 100), 3),
            **l,
            "role": "key" if c == KEY.lower() else "target" if c == TARGET.lower() else "feature",
        })
    meta = {
        "contract_version": "data-contract v1.0",
        "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_commit": _git_commit(),
        "seed": None,  # deterministic, no randomness
        "rows": {"train": len(train), "test": len(test)},
        **report,
    }
    Path(path).write_text(json.dumps({"meta": meta, "columns": cols}, indent=1, ensure_ascii=False), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/data.yaml")
    args = ap.parse_args(argv)
    train, test = build(load_config(args.config))
    print(f"train {train.shape} test {test.shape}")


if __name__ == "__main__":
    main()
