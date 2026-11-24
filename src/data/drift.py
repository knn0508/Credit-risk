"""Train vs test drift (PSI + SMD) -> docs/data/drift-report.md + data/interim/drift.json.

Descriptive only: test has no target and is never used for model/threshold selection (CLAUDE.md).
PSI: numeric -> train-decile bins (+ separate NaN bin); categorical/binary -> category shares (+ NaN, + unseen-in-train).
Rule of thumb: PSI <0.1 stable, 0.1-0.25 moderate, >0.25 large. Usage: python -m src.data.drift
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

EPS = 1e-4
SKIP = ("sk_id_curr", "target")


def _psi(p, q):
    p, q = np.clip(np.asarray(p, float), EPS, None), np.clip(np.asarray(q, float), EPS, None)
    return float(np.sum((q - p) * np.log(q / p)))


def psi_numeric(tr, te, bins=10):
    edges = np.unique(tr.dropna().quantile(np.linspace(0, 1, bins + 1)).to_numpy())
    if len(edges) < 3:  # near-constant: use category logic
        return psi_categorical(tr, te)
    edges[0], edges[-1] = -np.inf, np.inf

    def shares(s):
        idx = np.digitize(s.dropna().to_numpy(), edges[1:-1])
        c = np.bincount(idx, minlength=len(edges) - 1).astype(float)
        return np.append(c, s.isna().sum()) / len(s)
    return _psi(shares(tr), shares(te))


def psi_categorical(tr, te):
    cats = pd.Index(tr.dropna().unique())
    def shares(s):
        vc = s.value_counts(dropna=False)
        known = [vc.get(c, 0) for c in cats]
        unseen = s.notna().sum() - sum(vc.get(c, 0) for c in cats)
        return np.array(known + [unseen, s.isna().sum()], float) / len(s)
    return _psi(shares(tr), shares(te))


def drift_table(train, test):
    rows = []
    for c in train.columns:
        if c in SKIP or c not in test.columns:
            continue
        a, b = train[c], test[c]
        numeric = pd.api.types.is_numeric_dtype(a)
        binary = numeric and set(a.dropna().unique()) <= {0, 1}
        psi = psi_categorical(a, b) if (not numeric or binary) else psi_numeric(a, b)
        sd = a.std() if numeric else np.nan
        smd = float((a.mean() - b.mean()) / sd) if numeric and sd and sd == sd else None
        rows.append({"column": c, "kind": "numeric" if numeric and not binary else "categorical/binary",
                     "psi": round(psi, 5), "smd": None if smd is None else round(smd, 4),
                     "null_pct_train": round(float(a.isna().mean() * 100), 2),
                     "null_pct_test": round(float(b.isna().mean() * 100), 2)})
    return pd.DataFrame(rows).sort_values("psi", ascending=False).reset_index(drop=True)


def render(df, meta, cov):
    n = len(df)
    mod, large = int(((df.psi >= 0.1) & (df.psi < 0.25)).sum()), int((df.psi >= 0.25).sum())
    out = ["# Train vs Test drift (Agent 02, `python -m src.data.drift`)",
           f"Data versiyası: `{meta['data_version']}` · train {meta['rows']['train']:,} / test {meta['rows']['test']:,} · {n} sütun.",
           "Yalnız təsviri: test target-sizdir və model/hədd seçimində istifadə olunmur. PSI: <0.1 sabit, 0.1–0.25 orta, ≥0.25 böyük. "
           "Numerik PSI train desil bin-ləri ilə (NaN ayrıca bin), kateqorial PSI kateqoriya payları ilə (train-də olmayan kateqoriya ayrıca bin).",
           "", "## Xülasə", f"- PSI ≥ 0.25 (böyük): **{large}** sütun",
           f"- 0.1 ≤ PSI < 0.25 (orta): **{mod}** sütun", f"- PSI < 0.1 (sabit): **{n - mod - large}** sütun",
           f"- Maksimum PSI: {df.psi.iloc[0]} (`{df.column.iloc[0]}`)", f"- Orta PSI: {round(float(df.psi.mean()), 5)}",
           "", "## Ən çox sürüşən 25 sütun", "| sütun | növ | PSI | SMD | null% train | null% test |", "|---|---|---|---|---|---|"]
    for r in df.head(25).itertuples():
        out.append(f"| {r.column} | {r.kind} | {r.psi} | {'' if r.smd is None or r.smd != r.smd else r.smd} | {r.null_pct_train} | {r.null_pct_test} |")
    big_null = df[(df.null_pct_train - df.null_pct_test).abs() > 5]
    out += ["", "## Null nisbəti 5 faiz bəndindən çox fərqlənən sütunlar",
            ", ".join(f"`{c}`" for c in big_null.column) or "yoxdur"]
    out += ["", "## Əsas tapıntı: bureau_balance əhatəsi train və test-də fərqlidir",
            f"Bureau tarixçəsi olan müraciətlər arasında bureau_balance qeydi olanların payı: **train {cov['train']:.1%}**, **test {cov['test']:.1%}**. "
            "Xam fayllardan müstəqil yoxlanıb (bu build xətası deyil, datasetin xüsusiyyətidir). Nəticə: `bureau_months_*`, `bureau_dpd_*`, `bureau_has_bb_sum` "
            "aqreqatları train-də bureau müştərilərinin ~65%-i üçün NaN, test-də demək olar heç biri üçün NaN deyil. Bu sütunların PSI-si yüksək olmasının əsas səbəbi budur "
            "(dəyərlərin yox, itkinin sürüşməsi).",
            "**Tövsiyə:** 04/05 bu sütunları feature-a daxil edəndə (a) itkin pattern-in train-də target ilə əlaqəsini yoxlasın, (b) bu sütunlarsız baseline ilə müqayisə etsin, "
            "(c) validation nəticələrini test paylanmasına ötürməsin; model train itkisini 'bureau_balance yoxdur' siqnalı kimi öyrənə bilər ki, test-də mövcud deyil. "
            "Qərar 04/05/01-indir; data qatında silinmir.",
            "", "## Şərh (05/04 üçün)",
            "- Test-in null pattern-i train ilə müqayisə olunur: böyük null fərqi imputasiya/indikator qərarlarına təsir edə bilər.",
            "- Sürüşmə yüksək olan sütunlar üçün model performansının sabitliyi 05-in validation-ında ayrıca yoxlanmalıdır (test labelsizdir, ona görə yalnız paylanma müqayisəsidir).",
            "- Bu sürüşmə həm də məlum Kaggle split xüsusiyyətidir; real istehsal drift monitorinqi üçün eyni PSI funksiyaları `src/data/drift.py`-dən istifadə oluna bilər."]
    return "\n".join(out) + "\n"


def main():
    pdir = Path("data/processed")
    train = pd.read_parquet(pdir / "application_train.parquet")
    test = pd.read_parquet(pdir / "application_test.parquet")
    meta = json.loads((pdir / "schema.json").read_text(encoding="utf-8"))["meta"]
    df = drift_table(train, test)
    cov = {n: float((d.bureau_has_bb_sum[d.bureau_has_history == 1] > 0).mean()) for n, d in (("train", train), ("test", test))}
    Path("data/interim").mkdir(exist_ok=True)
    df.to_json("data/interim/drift.json", orient="records", indent=1)
    Path("docs/data/drift-report.md").write_text(render(df, meta, cov), encoding="utf-8")
    print(f"{len(df)} columns; PSI>=0.25: {(df.psi >= 0.25).sum()}, 0.1-0.25: {((df.psi >= 0.1) & (df.psi < 0.25)).sum()}")


if __name__ == "__main__":
    main()
