"""Data quality audit -> docs/data/quality-report.md + data/interim/audit.json.

Checks: sentinels/XNA, impossible values, constants, duplicates, referential integrity,
train/test schema + shift. Read-only on raw data. Usage: python -m src.data.audit
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from src.data.inventory import load_config

SENTINEL_DAYS = 365243  # Home Credit placeholder for "not applicable" in DAYS_* columns

# child table -> (file, id columns to load)
CHILD = {
    "bureau": ["SK_ID_CURR", "SK_ID_BUREAU"],
    "previous_application": ["SK_ID_CURR", "SK_ID_PREV"],
    "POS_CASH_balance": ["SK_ID_CURR", "SK_ID_PREV"],
    "credit_card_balance": ["SK_ID_CURR", "SK_ID_PREV"],
    "installments_payments": ["SK_ID_CURR", "SK_ID_PREV"],
}


def app_checks(train, test):
    out = {}
    out["train_rows"], out["test_rows"] = len(train), len(test)
    out["train_id_unique"] = bool(train.SK_ID_CURR.is_unique)
    out["test_id_unique"] = bool(test.SK_ID_CURR.is_unique)
    out["id_overlap_train_test"] = int(train.SK_ID_CURR.isin(test.SK_ID_CURR).sum())
    out["full_row_duplicates_train"] = int(train.duplicated().sum())
    out["target_rate"] = round(float(train.TARGET.mean()), 5)
    out["target_values"] = sorted(train.TARGET.dropna().unique().tolist())
    out["target_nulls"] = int(train.TARGET.isna().sum())
    out["schema_train_minus_test"] = sorted(set(train.columns) - set(test.columns))
    out["schema_test_minus_train"] = sorted(set(test.columns) - set(train.columns))
    out["dtype_mismatch"] = {
        c: [str(train[c].dtype), str(test[c].dtype)]
        for c in train.columns if c in test.columns and train[c].dtype != test[c].dtype
    }
    out["constant_columns"] = [c for c in train.columns if train[c].nunique(dropna=False) <= 1]
    days = [c for c in train.columns if c.startswith("DAYS_")]
    out["days_sentinel_365243"] = {
        c: int((train[c] == SENTINEL_DAYS).sum()) for c in days if (train[c] == SENTINEL_DAYS).any()
    }
    out["days_positive_non_sentinel"] = {
        c: int(((train[c] > 0) & (train[c] != SENTINEL_DAYS)).sum())
        for c in days if ((train[c] > 0) & (train[c] != SENTINEL_DAYS)).any()
    }
    strs = [c for c in train.columns if not pd.api.types.is_numeric_dtype(train[c])]
    out["xna_counts_train"] = {c: int((train[c] == "XNA").sum()) for c in strs if (train[c] == "XNA").any()}
    out["age_years_range"] = [round(float(-train.DAYS_BIRTH.max() / 365.25), 1),
                              round(float(-train.DAYS_BIRTH.min() / 365.25), 1)]
    out["income_max"] = float(train.AMT_INCOME_TOTAL.max())
    out["income_nonpositive"] = int((train.AMT_INCOME_TOTAL <= 0).sum())
    out["cnt_children_max"] = int(train.CNT_CHILDREN.max())
    out["cnt_fam_members_lt1"] = int((train.CNT_FAM_MEMBERS < 1).sum())
    out["obs_30_cnt_social_circle_max"] = float(train.OBS_30_CNT_SOCIAL_CIRCLE.max())
    # normalised-score / flag columns outside plausible range
    out["ext_source_out_of_0_1"] = {
        c: int(((train[c] < 0) | (train[c] > 1)).sum()) for c in train.columns if c.startswith("EXT_SOURCE")
    }
    out["amt_req_credit_bureau_nulls_pct"] = round(float(train.AMT_REQ_CREDIT_BUREAU_YEAR.isna().mean() * 100), 2)
    # train/test shift: standardised mean difference on numeric columns
    num = [c for c in train.columns if c in test.columns and pd.api.types.is_numeric_dtype(train[c])
           and c != "SK_ID_CURR"]
    smd = {}
    for c in num:
        s = train[c].std()
        if s and s == s:
            smd[c] = round(float((train[c].mean() - test[c].mean()) / s), 4)
    out["train_test_smd_top"] = dict(sorted(smd.items(), key=lambda kv: -abs(kv[1]))[:10])
    return out


def referential(app_ids_train, app_ids_test):
    app_ids = set(app_ids_train) | set(app_ids_test)
    res = {}
    for name, cols in CHILD.items():
        df = pd.read_csv(f"{RAW}/{name}.csv", usecols=cols)
        cur = df.SK_ID_CURR
        r = {
            "rows": len(df),
            "id_null": int(cur.isna().sum()),
            "orphan_rows_not_in_application": int((~cur.isin(app_ids)).sum()),
            "distinct_curr": int(cur.nunique()),
            "curr_in_train": int(pd.Series(cur.unique()).isin(app_ids_train).sum()),
            "curr_in_test": int(pd.Series(cur.unique()).isin(app_ids_test).sum()),
        }
        if "SK_ID_PREV" in cols:
            r["distinct_prev"] = int(df.SK_ID_PREV.nunique())
            # SK_ID_PREV should map to exactly one SK_ID_CURR
            r["prev_with_multiple_curr"] = int((df.groupby("SK_ID_PREV").SK_ID_CURR.nunique() > 1).sum())
        if name == "bureau":
            r["bureau_id_unique"] = bool(df.SK_ID_BUREAU.is_unique)
            bureau_ids = set(df.SK_ID_BUREAU)
        if name == "previous_application":
            r["prev_id_unique"] = bool(df.SK_ID_PREV.is_unique)
            prev_curr = df.set_index("SK_ID_PREV").SK_ID_CURR
        res[name] = r
    bb = pd.read_csv(f"{RAW}/bureau_balance.csv", usecols=["SK_ID_BUREAU", "MONTHS_BALANCE"])
    res["bureau_balance"] = {
        "rows": len(bb),
        "orphan_rows_not_in_bureau": int((~bb.SK_ID_BUREAU.isin(bureau_ids)).sum()),
        "duplicate_bureau_month": int(bb.duplicated().sum()),
        "months_balance_positive": int((bb.MONTHS_BALANCE > 0).sum()),
    }
    # SK_ID_CURR in child tables must agree with previous_application's owner
    for name in ("POS_CASH_balance", "credit_card_balance", "installments_payments"):
        df = pd.read_csv(f"{RAW}/{name}.csv", usecols=["SK_ID_CURR", "SK_ID_PREV"]).drop_duplicates()
        owner = df.SK_ID_PREV.map(prev_curr)
        res[name]["prev_not_in_previous_application"] = int(owner.isna().sum())
        res[name]["curr_mismatch_with_previous_application"] = int(((owner != df.SK_ID_CURR) & owner.notna()).sum())
    return res


def child_value_checks():
    """Leakage-relevant sign checks: history must be in the past (DAYS_* <= 0)."""
    res = {}
    bu = pd.read_csv(f"{RAW}/bureau.csv", usecols=["DAYS_CREDIT", "DAYS_CREDIT_ENDDATE", "DAYS_ENDDATE_FACT"])
    res["bureau_days_credit_positive"] = int((bu.DAYS_CREDIT > 0).sum())
    res["bureau_days_credit_enddate_positive(future-dated, ok)"] = int((bu.DAYS_CREDIT_ENDDATE > 0).sum())
    res["bureau_days_enddate_fact_positive"] = int((bu.DAYS_ENDDATE_FACT > 0).sum())
    pa = pd.read_csv(f"{RAW}/previous_application.csv", usecols=[
        "DAYS_DECISION", "DAYS_FIRST_DRAWING", "DAYS_FIRST_DUE", "DAYS_LAST_DUE_1ST_VERSION",
        "DAYS_LAST_DUE", "DAYS_TERMINATION", "NAME_CONTRACT_STATUS"])
    for c in ["DAYS_FIRST_DRAWING", "DAYS_FIRST_DUE", "DAYS_LAST_DUE_1ST_VERSION", "DAYS_LAST_DUE", "DAYS_TERMINATION"]:
        res[f"prev_{c.lower()}_sentinel_365243"] = int((pa[c] == SENTINEL_DAYS).sum())
        res[f"prev_{c.lower()}_positive_non_sentinel"] = int(((pa[c] > 0) & (pa[c] != SENTINEL_DAYS)).sum())
    res["prev_days_decision_positive"] = int((pa.DAYS_DECISION > 0).sum())
    res["prev_status_counts"] = pa.NAME_CONTRACT_STATUS.value_counts().to_dict()
    ip = pd.read_csv(f"{RAW}/installments_payments.csv")
    res["inst_days_entry_payment_positive"] = int((ip.DAYS_ENTRY_PAYMENT > 0).sum())
    res["inst_full_row_duplicates"] = int(ip.duplicated().sum())
    res["inst_amt_payment_zero_or_null"] = int((ip.AMT_PAYMENT.fillna(0) == 0).sum())
    pos = pd.read_csv(f"{RAW}/POS_CASH_balance.csv", usecols=["MONTHS_BALANCE", "NAME_CONTRACT_STATUS"])
    res["pos_months_balance_positive"] = int((pos.MONTHS_BALANCE > 0).sum())
    res["pos_status_counts"] = pos.NAME_CONTRACT_STATUS.value_counts().to_dict()
    cc = pd.read_csv(f"{RAW}/credit_card_balance.csv", usecols=["MONTHS_BALANCE", "AMT_BALANCE", "AMT_DRAWINGS_CURRENT"])
    res["cc_months_balance_positive"] = int((cc.MONTHS_BALANCE > 0).sum())
    res["cc_amt_drawings_negative"] = int((cc.AMT_DRAWINGS_CURRENT < 0).sum())
    return res


def main(argv=None):
    global RAW
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/data.yaml")
    ap.add_argument("--out", default="data/interim/audit.json")
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    RAW = cfg["raw_dir"]
    train = pd.read_csv(f"{RAW}/application_train.csv")
    test = pd.read_csv(f"{RAW}/application_test.csv")
    result = {"application": app_checks(train, test)}
    result["referential"] = referential(set(train.SK_ID_CURR), set(test.SK_ID_CURR))
    result["child_values"] = child_value_checks()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, default=str), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
