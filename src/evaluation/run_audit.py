"""Subgroup audit runner (gender, age, education, family, occupation, organization, region, children).
Usage: python -m src.evaluation.run_audit <bundle_dir> <low_max> <medium_max> [oof|holdout]
Default source 'oof' (train part). 'holdout' only for the FINAL report, after thresholds are frozen.
Statistical audit, not proof of fairness. Writes reports/subgroups_<version>_<source>.md
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd

from .subgroups import age_groups, audit

def to_md(df: pd.DataFrame) -> str:
    """Minimal markdown table (no tabulate dependency)."""
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


COLS = ["code_gender", "name_education_type", "name_family_status", "occupation_type",
        "organization_type", "region_rating_client", "cnt_children", "days_birth"]


def build_frame(bundle: Path, source: str = "oof") -> pd.DataFrame:
    if source != "oof":
        raise NotImplementedError("holdout scoring is done in the final report step, after thresholds are frozen")
    oof = pd.read_parquet(bundle / "oof_predictions.parquet")
    cal = joblib.load(bundle / "calibrator.joblib")
    d = pd.read_parquet("data/processed/application_train.parquet", columns=["sk_id_curr", *COLS])
    df = oof.merge(d, on="sk_id_curr", how="left", validate="1:1")
    assert len(df) == len(oof), "row count changed in join"
    df["p_cal"] = cal.predict(df.p_raw)
    df["age_group"] = age_groups(df.days_birth)
    df["children_group"] = df.cnt_children.clip(upper=3).astype("Int64").astype(str).replace("3", "3+")
    return df


def main(bundle: str, low_max: float, medium_max: float, source: str = "oof") -> str:
    b = Path(bundle)
    df = build_frame(b, source)
    parts = [f"# Subgroup audit — {b.name} ({source})\n",
             f"Hədlər (fərziyyə): low_max={low_max}, medium_max={medium_max}. Statistik audit, ədalətlilik sübutu deyil. "
             "Kiçik qruplar (n<100 və ya <10 müsbət): AUC 'insufficient'.\n"]
    for g in ["code_gender", "age_group", "name_education_type", "name_family_status", "occupation_type",
              "organization_type", "region_rating_client", "children_group"]:
        parts.append(f"\n## {g}\n\n" + audit(df, g, low_max, medium_max).round(4).pipe(to_md) + "\n")
    out = Path("reports") / f"subgroups_{b.name}_{source}.md"
    out.write_text("\n".join(parts), encoding="utf-8")
    return str(out)


if __name__ == "__main__":
    print(main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), *(sys.argv[4:5])))
