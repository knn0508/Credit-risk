"""Child-table -> SK_ID_CURR aggregation (data-contract v1.0).

Every function takes a raw child DataFrame and returns (agg_df, lineage):
  agg_df  : one row per SK_ID_CURR (unique index), columns `<source>_<column>_<stat>`
  lineage : {output_column: {"source_table", "source_column", "stat"}}
Only history known at application time is used (DAYS_* <= 0). Excluded per contract item 6:
previous_application DAYS_LAST_DUE_1ST_VERSION / DAYS_LAST_DUE / DAYS_TERMINATION / DAYS_FIRST_DRAWING.
"""
import numpy as np
import pandas as pd

KEY = "SK_ID_CURR"
SENTINEL_DAYS = 365243


def _agg(df, by, table, prefix, spec):
    """spec: {source_col: [stats]}; returns frame indexed by `by` + lineage."""
    named = {}
    lineage = {}
    for col, stats in spec.items():
        for stat in stats:
            out = f"{prefix}_{col.lower()}_{stat}"
            named[out] = pd.NamedAgg(column=col, aggfunc=stat)
            lineage[out] = {"source_table": table, "source_column": col, "stat": stat}
    g = df.groupby(by)
    out = g.agg(**named)
    # pandas sums an all-NaN group to 0; "nothing observed" must stay NaN (contract item 5)
    for col in {c for c, stats in spec.items() if "sum" in stats}:
        out.loc[g[col].count() == 0, f"{prefix}_{col.lower()}_sum"] = np.nan
    return out, lineage


def aggregate_bureau_balance(bb):
    """SK_ID_BUREAU level (not SK_ID_CURR): months, dpd-status counts/shares."""
    bb = bb.assign(
        is_dpd=bb.STATUS.isin(["1", "2", "3", "4", "5"]).astype("int8"),
        is_closed=(bb.STATUS == "C").astype("int8"),
        is_unknown=(bb.STATUS == "X").astype("int8"),
        is_dpd_severe=bb.STATUS.isin(["3", "4", "5"]).astype("int8"),
    )
    g = bb.groupby("SK_ID_BUREAU")
    out = pd.DataFrame({
        "months_count": g.size(),
        "months_oldest": -g.MONTHS_BALANCE.min(),
        "dpd_months": g.is_dpd.sum(),
        "dpd_severe_months": g.is_dpd_severe.sum(),
        "closed_months": g.is_closed.sum(),
        "unknown_months": g.is_unknown.sum(),
    })
    out["dpd_share"] = out.dpd_months / out.months_count
    return out


def aggregate_bureau(bureau, bb_by_bureau):
    n0 = len(bureau)
    # bureau_balance -> bureau level (left join, bureau grain SK_ID_BUREAU must stay unique)
    assert bb_by_bureau.index.is_unique and bureau.SK_ID_BUREAU.is_unique
    b = bureau.merge(bb_by_bureau, how="left", left_on="SK_ID_BUREAU", right_index=True)
    assert len(b) == n0, "bureau row count changed after bureau_balance join"
    b["active"] = (b.CREDIT_ACTIVE == "Active").astype("int8")
    b["closed"] = (b.CREDIT_ACTIVE == "Closed").astype("int8")
    b["has_overdue"] = (b.CREDIT_DAY_OVERDUE > 0).astype("int8")
    b["has_bb"] = b.months_count.notna().astype("int8")
    spec = {
        "SK_ID_BUREAU": ["count"],
        "active": ["sum", "mean"],
        "closed": ["sum"],
        "has_overdue": ["sum"],
        "DAYS_CREDIT": ["min", "max", "mean"],
        "CREDIT_DAY_OVERDUE": ["max", "mean"],
        "DAYS_CREDIT_ENDDATE": ["min", "max"],
        "AMT_CREDIT_MAX_OVERDUE": ["max"],
        "CNT_CREDIT_PROLONG": ["sum", "max"],
        "AMT_CREDIT_SUM": ["sum", "mean", "max"],
        "AMT_CREDIT_SUM_DEBT": ["sum", "max"],
        "AMT_CREDIT_SUM_LIMIT": ["sum"],
        "AMT_CREDIT_SUM_OVERDUE": ["sum", "max"],
        "AMT_ANNUITY": ["sum", "mean"],
        # bureau_balance, already collapsed per SK_ID_BUREAU
        "has_bb": ["sum"],
        "months_count": ["sum", "max"],
        "months_oldest": ["max"],
        "dpd_months": ["sum", "max"],
        "dpd_severe_months": ["sum"],
        "dpd_share": ["mean", "max"],
    }
    agg, lin = _agg(b, KEY, "bureau", "bureau", spec)
    # honest lineage for bureau_balance-derived columns
    for c, l in lin.items():
        if l["source_column"] in ("has_bb", "months_count", "months_oldest", "dpd_months",
                                  "dpd_severe_months", "dpd_share"):
            l["source_table"] = "bureau_balance"
            l["source_column"] = {"has_bb": "SK_ID_BUREAU", "months_count": "MONTHS_BALANCE",
                                  "months_oldest": "MONTHS_BALANCE", "dpd_months": "STATUS",
                                  "dpd_severe_months": "STATUS", "dpd_share": "STATUS"}[l["source_column"]]
        if l["source_column"] in ("active", "closed", "has_overdue"):
            l["source_column"] = {"active": "CREDIT_ACTIVE", "closed": "CREDIT_ACTIVE",
                                  "has_overdue": "CREDIT_DAY_OVERDUE"}[l["source_column"]]
    # categorical diversity
    agg["bureau_credit_type_nunique"] = b.groupby(KEY).CREDIT_TYPE.nunique()
    lin["bureau_credit_type_nunique"] = {"source_table": "bureau", "source_column": "CREDIT_TYPE", "stat": "nunique"}
    return agg, lin


def aggregate_previous_application(pa):
    pa = pa.copy()
    # sentinel hygiene (contract item 2); excluded leakage columns are never aggregated (item 6)
    pa.loc[pa.DAYS_DECISION == SENTINEL_DAYS, "DAYS_DECISION"] = np.nan
    st = pa.NAME_CONTRACT_STATUS
    pa["approved"] = (st == "Approved").astype("int8")
    pa["refused"] = (st == "Refused").astype("int8")
    pa["canceled"] = (st == "Canceled").astype("int8")
    spec = {
        "SK_ID_PREV": ["count"],
        "approved": ["sum", "mean"],
        "refused": ["sum", "mean"],
        "canceled": ["sum"],
        "AMT_APPLICATION": ["mean", "max", "sum"],
        "AMT_CREDIT": ["mean", "max", "sum"],
        "AMT_ANNUITY": ["mean", "max"],
        "AMT_DOWN_PAYMENT": ["mean", "max"],
        "AMT_GOODS_PRICE": ["mean", "max"],
        "RATE_DOWN_PAYMENT": ["mean"],
        "CNT_PAYMENT": ["mean", "max"],
        "DAYS_DECISION": ["min", "max", "mean"],
    }
    agg, lin = _agg(pa, KEY, "previous_application", "previous_application", spec)
    for c, l in lin.items():
        if l["source_column"] in ("approved", "refused", "canceled"):
            l["source_column"] = "NAME_CONTRACT_STATUS"
    return agg, lin


def aggregate_pos_cash(pos):
    pos = pos.assign(completed=(pos.NAME_CONTRACT_STATUS == "Completed").astype("int8"))
    spec = {
        "SK_ID_PREV": ["count", "nunique"],
        "MONTHS_BALANCE": ["min", "max"],
        "CNT_INSTALMENT": ["mean", "max"],
        "CNT_INSTALMENT_FUTURE": ["mean", "min"],
        "SK_DPD": ["max", "mean"],
        "SK_DPD_DEF": ["max", "mean"],
        "completed": ["sum"],
    }
    agg, lin = _agg(pos, KEY, "POS_CASH_balance", "pos_cash_balance", spec)
    for c, l in lin.items():
        if l["source_column"] == "completed":
            l["source_column"] = "NAME_CONTRACT_STATUS"
    return agg, lin


def aggregate_credit_card(cc):
    cc = cc.copy()
    cc["AMT_DRAWINGS_CURRENT"] = cc.AMT_DRAWINGS_CURRENT.clip(lower=0)  # 3 negative rows (audit)
    spec = {
        "SK_ID_PREV": ["count", "nunique"],
        "MONTHS_BALANCE": ["min"],
        "AMT_BALANCE": ["mean", "max"],
        "AMT_CREDIT_LIMIT_ACTUAL": ["mean", "max"],
        "AMT_DRAWINGS_CURRENT": ["sum", "mean"],
        "AMT_PAYMENT_CURRENT": ["sum", "mean"],
        "AMT_RECEIVABLE_PRINCIPAL": ["mean", "max"],
        "SK_DPD": ["max", "mean"],
        "SK_DPD_DEF": ["max", "mean"],
    }
    return _agg(cc, KEY, "credit_card_balance", "credit_card_balance", spec)


def aggregate_installments(ip):
    ip = ip.assign(
        days_late=ip.DAYS_ENTRY_PAYMENT - ip.DAYS_INSTALMENT,  # >0 = paid after due date
        amt_unpaid=(ip.AMT_INSTALMENT - ip.AMT_PAYMENT).clip(lower=0),
    )
    ip["is_late"] = (ip.days_late > 0).astype("int8")
    spec = {
        "SK_ID_PREV": ["count", "nunique"],
        "NUM_INSTALMENT_NUMBER": ["max"],
        "AMT_INSTALMENT": ["sum", "mean", "max"],
        "AMT_PAYMENT": ["sum", "mean"],
        "days_late": ["max", "mean"],
        "is_late": ["sum", "mean"],
        "amt_unpaid": ["sum", "max"],
    }
    agg, lin = _agg(ip, KEY, "installments_payments", "installments_payments", spec)
    for c, l in lin.items():
        l["source_column"] = {"days_late": "DAYS_ENTRY_PAYMENT-DAYS_INSTALMENT",
                              "is_late": "DAYS_ENTRY_PAYMENT-DAYS_INSTALMENT",
                              "amt_unpaid": "AMT_INSTALMENT-AMT_PAYMENT"}.get(l["source_column"], l["source_column"])
    return agg, lin
