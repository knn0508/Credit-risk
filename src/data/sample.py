"""Input schema + synthetic demo applicants for 06 (API/UI).

Outputs (aggregate statistics and synthetic rows only; NO real raw rows):
  docs/data/sample-schema.json     field, group, kind, nullable, allowed values / ranges
  docs/data/sample-applicants.json synthetic /predict-style requests (seed=42)
Samples draw each column from its train marginal (categories by frequency, numbers uniform in [p05, p95]);
has_history / sentinel-flag consistency is enforced. They are for plumbing and UI demos, NOT model-quality checks.
Usage: python -m src.data.sample
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.data.inventory import load_config

SEED = 42
N_SAMPLES = 20
EXCLUDED_FROM_INPUT = ("target",)  # never an input
OPTIONAL_KEY = "sk_id_curr"
FLAG_GROUPS = ("bureau", "previous_application", "pos_cash_balance", "credit_card_balance", "installments_payments")


def _kind(s):
    if not pd.api.types.is_numeric_dtype(s):
        return "categorical"
    vals = s.dropna().unique()
    if len(vals) <= 2 and set(vals) <= {0, 1}:
        return "binary"
    return "integer" if pd.api.types.is_integer_dtype(s) or np.all(np.mod(vals, 1) == 0) else "float"


def build_input_schema(train, schema_cols):
    meta = {c["column"]: c for c in schema_cols}
    fields = []
    for c in train.columns:
        if c in EXCLUDED_FROM_INPUT:
            continue
        s, k = train[c], _kind(train[c])
        f = {"name": c, "kind": k, "dtype": str(s.dtype), "nullable": bool(s.isna().any()),
             "null_pct": round(float(s.isna().mean() * 100), 3), "required": False,
             "group": "application" if meta[c]["source_table"].startswith("application") else "aggregate",
             "source_table": meta[c]["source_table"]}
        if c == OPTIONAL_KEY:
            f["note"] = "optional identifier; not a model feature"
        if c == "code_gender":
            f["note"] = "protected attribute (decisions/0002): accepted, excluded from model features"
        if k == "categorical":
            f["allowed_values"] = sorted(s.dropna().unique().tolist())
        elif k == "binary":
            f["allowed_values"] = [0, 1]
        else:
            q = s.quantile([0.01, 0.05, 0.95, 0.99])
            f.update(min=float(s.min()), max=float(s.max()), p01=float(q[0.01]), p99=float(q[0.99]),
                     p05=float(q[0.05]), p95=float(q[0.95]))
        fields.append(f)
    return fields


def synth_applicants(train, fields, n=N_SAMPLES, seed=SEED):
    rng = np.random.default_rng(seed)
    cols = {}
    for f in fields:
        c, k = f["name"], f["kind"]
        if c == OPTIONAL_KEY:
            continue
        if k in ("categorical", "binary"):
            vc = train[c].value_counts(normalize=True)
            cols[c] = rng.choice(vc.index.to_numpy(dtype=object), size=n, p=vc.to_numpy())
        else:
            v = rng.uniform(f["p05"], f["p95"], size=n)
            cols[c] = np.round(v) if k == "integer" else np.round(v, 3)
    df = pd.DataFrame(cols).astype(object)
    # nulls at the train null rate
    for f in fields:
        c = f["name"]
        if c in df and f["nullable"] and f["null_pct"] > 0:
            df.loc[rng.random(n) < f["null_pct"] / 100, c] = None
    # consistency: no history -> counts 0, flag 0, other aggregates null
    for g in FLAG_GROUPS:
        flag = f"{g}_has_history"
        none = df[flag].astype(int) == 0
        for f in fields:
            c = f["name"]
            if f["group"] != "aggregate" or not c.startswith(g + "_") or c == flag:
                continue
            is_count = c.endswith(("_count", "_nunique"))
            df.loc[none, c] = 0 if is_count else None
    # anomaly flag -> days_employed null
    df.loc[df.days_employed_is_anomalous.astype(int) == 1, "days_employed"] = None
    # clip to observed range so values stay valid; keep nulls as None, integers as int
    def fit(x, lo, hi, integer):
        if x is None or x != x:
            return None
        x = min(max(float(x), lo), hi)
        return int(x) if integer else x

    for f in fields:
        c = f["name"]
        if f["kind"] in ("integer", "float") and c in df:
            vals = [fit(x, f["min"], f["max"], f["kind"] == "integer") for x in df[c]]
            df[c] = pd.Series(vals, index=df.index, dtype=object)
    return df


def to_records(df):
    def clean(v):
        if v is None or (isinstance(v, float) and v != v):
            return None
        return v.item() if hasattr(v, "item") else v
    return [{c: clean(v) for c, v in row.items()} for row in df.to_dict("records")]


def main():
    cfg = load_config("configs/data.yaml")
    pdir = Path(cfg["processed_dir"])
    train = pd.read_parquet(pdir / "application_train.parquet")
    sch = json.loads((pdir / "schema.json").read_text(encoding="utf-8"))
    fields = build_input_schema(train, sch["columns"])
    samples = to_records(synth_applicants(train, fields))
    out = Path("docs/data")
    doc = {"contract_version": sch["meta"]["contract_version"], "data_version": sch["meta"]["data_version"],
           "note": "Every field is optional (missing -> null + warning). `target` is never an input. "
                   "Fields come from data/processed schema; names are model-independent (feature_names in the bundle decide what the model uses).",
           "n_fields": len(fields), "fields": fields}
    (out / "sample-schema.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    req = {"note": f"SYNTHETIC applicants (seed={SEED}); marginals only, not real rows, not for model-quality checks.",
           "requests": [{"applicant": a, "request_id": f"demo-{i:03d}"} for i, a in enumerate(samples)]}
    (out / "sample-applicants.json").write_text(json.dumps(req, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(fields)} fields, {len(samples)} synthetic applicants")


if __name__ == "__main__":
    main()
