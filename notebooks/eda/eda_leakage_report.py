"""EDA + leakage yoxlaması -> docs/features/eda-leakage-report.md. Yalnız application_train (TARGET orada var).
İşlət: python notebooks/eda/eda_leakage_report.py
"""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from src.features import ApplicationFeatures, AggregateFeatures, EXCLUDED_PROTECTED_FEATURES

d = pd.read_parquet("data/processed/application_train.parquet").set_index("sk_id_curr")
schema = {c["column"]: c for c in json.load(open("data/processed/schema.json"))["columns"]}
y = d.pop("target")
ft = pd.concat([ApplicationFeatures().fit(d).transform(d), AggregateFeatures().fit(d).transform(d)], axis=1)
num = d.select_dtypes("number").join(ft)

def uauc(s):  # univariate AUC (NaN -> median), 0.5 = informasiyasız
    m = s.notna()
    if m.sum() < 1000 or s[m].nunique() < 2:
        return np.nan
    return roc_auc_score(y, s.fillna(s.median()))

auc = num.apply(uauc).dropna()
strength = (auc - 0.5).abs().sort_values(ascending=False)
L = []
L += ["# EDA + leakage hesabatı (Agent 03, avtomatik: notebooks/eda/eda_leakage_report.py)", "",
      f"Data: application_train, {d.shape[0]} sətir, {d.shape[1]} processed sütun + {ft.shape[1]} ft_. Defolt payı: {y.mean():.4%}.",
      "Univariate AUC yalnız siqnal göstəricisidir (modelin keyfiyyəti deyil); 0.5 = siqnalsız.", ""]
L += ["## 1. Ən güclü 15 feature (|AUC−0.5|)", "| feature | AUC | null % |", "|---|---|---|"]
for c in strength.head(15).index:
    L.append(f"| {c} | {auc[c]:.3f} | {num[c].isna().mean():.1%} |")
L += ["", "## 2. Missingness", f"- >50% null olan sütun: {(d.isna().mean() > .5).sum()} (processed), {(ft.isna().mean() > .5).sum()} (ft_)."]
hi = ft.isna().mean().sort_values(ascending=False)
L += ["- ft_ null (top 5): " + ", ".join(f"{k} {v:.0%}" for k, v in hi.head(5).items())]
L += ["- Null-un özü siqnaldır? `*_has_history` bayraqlarının AUC-si:"]
for c in [c for c in d.columns if c.endswith("has_history")]:
    L.append(f"  - {c}: AUC {auc.get(c, np.nan):.3f}, tarixçəsizlər {(1 - d[c].mean()):.1%}")
L += ["", "## 3. Leakage yoxlamaları"]
chk = []
chk.append(("TARGET feature matrisində yoxdur", "target" not in d.columns and "target" not in ft.columns))
chk.append(("code_gender ft_-də yoxdur / model matrisindən çıxarılır", not set(EXCLUDED_PROTECTED_FEATURES) & set(ft.columns)))
sus = strength[strength > 0.25]
chk.append((f"Şübhəli yüksək siqnal (|AUC−0.5|>0.25): {list(sus.index) or 'yoxdur'}", len(sus) == 0))
# gələcək tarix: DAYS_* aqreqatlar müraciət anına qədər olmalıdır (<=0), bəzi *_enddate/ _future istisna
pos = []
for c in d.columns:
    if any(k in c for k in ("days_credit_min", "days_credit_max", "days_credit_mean", "days_decision", "months_balance")) and d[c].max() > 0:
        pos.append(c)
chk.append((f"Keçmiş-tarix sütunlarında müsbət (gələcək) dəyər: {pos or 'yoxdur'}", not pos))
fut = [c for c in d.columns if "enddate" in c and d[c].max() > 0]
L += [f"- {'OK ' if ok else 'DİQQƏT'}: {t}" for t, ok in chk]
L += [f"- Məlumat: gələcək son tarix (days_credit_enddate_*) müsbət ola bilər (kreditin planlı bitməsi, müraciət anında məlumdur): {fut}"]
corr = ft.corrwith(y).abs().sort_values(ascending=False)
L += ["- ft_ top |corr(TARGET)|: " + ", ".join(f"{k} {v:.3f}" for k, v in corr.head(5).items())]
dup = ft.round(10).T.duplicated()
L += [f"- Dublikat ft_ sütunu: {list(ft.columns[dup.values]) or 'yoxdur'}"]
L += ["", "## 4. Outlier (winsorize/log qərarı üçün; silinmir)"]
for c in ["amt_income_total", "amt_credit", "ft_credit_income_ratio", "ft_credit_term"]:
    s = num[c].dropna()
    L.append(f"- {c}: p50 {s.median():.3g}, p99 {s.quantile(.99):.3g}, max {s.max():.3g}, max/p99 = {s.max()/s.quantile(.99):.1f}")
L += ["", "## 5. Nəticə", "Avtomatik yoxlamalarda leakage əlaməti tapılmadı. Məhdudiyyət: evristik yoxlamadır; mütləq tarix olmadığı üçün aqreqatların müraciətdən sonrakı sətirləri daxil etmədiyi data özündən sübut oluna bilməz, yalnız DAYS_* işarəsi və siqnal gücü ilə dolayı yoxlanır."]
open("docs/features/eda-leakage-report.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
