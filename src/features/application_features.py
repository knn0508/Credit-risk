"""Catalogue bölmə A: application sütunlarından ft_ feature-lar.

Stateless (fit öyrənmir) -> leakage riski yoxdur; train və inference eyni kod.
Giriş: data-contract-a görə kiçik hərfli sütunlar. TARGET istifadə olunmur.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

DAYS_EMPLOYED_ANOM = 365243
EXT = ["ext_source_1", "ext_source_2", "ext_source_3"]
DOCS = [f"flag_document_{i}" for i in range(2, 22)]
REQ = [f"amt_req_credit_bureau_{s}" for s in ("hour", "day", "week", "mon", "qrt", "year")]

FEATURE_NAMES = [
    "ft_credit_income_ratio", "ft_annuity_income_ratio", "ft_credit_term",
    "ft_credit_goods_ratio", "ft_age_years", "ft_employed_years",
    "ft_employed_age_ratio", "ft_income_per_person", "ft_ext_source_mean",
    "ft_ext_source_min", "ft_ext_source_prod", "ft_ext_source_missing_cnt",
    "ft_doc_count", "ft_bureau_req_total_year", "ft_days_registration_years",
    "ft_id_publish_years",
]


def _ratio(a: pd.Series, b: pd.Series) -> pd.Series:
    b = b.where(b > 0)  # b<=0 -> NaN
    return a / b


class ApplicationFeatures(BaseEstimator, TransformerMixin):
    """Qaytarır: yalnız ft_ sütunları, sabit sıra (FEATURE_NAMES), index saxlanır."""

    def fit(self, X, y=None):
        self.feature_names_ = list(FEATURE_NAMES)
        return self

    def get_feature_names_out(self, input_features=None):
        return np.array(FEATURE_NAMES, dtype=object)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        d = X
        out = pd.DataFrame(index=d.index)
        out["ft_credit_income_ratio"] = _ratio(d["amt_credit"], d["amt_income_total"])
        out["ft_annuity_income_ratio"] = _ratio(d["amt_annuity"], d["amt_income_total"])
        out["ft_credit_term"] = _ratio(d["amt_credit"], d["amt_annuity"])
        out["ft_credit_goods_ratio"] = _ratio(d["amt_credit"], d["amt_goods_price"])
        age = -d["days_birth"] / 365.25
        # data-contract v1.0: processed-də sentinel artıq NaN + days_employed_is_anomalous bayrağı;
        # xam (365243) giriş də dəstəklənir.
        anom = d["days_employed"] == DAYS_EMPLOYED_ANOM
        if "days_employed_is_anomalous" in d.columns:
            anom = anom | d["days_employed_is_anomalous"].fillna(0).astype(bool)
        emp = (-d["days_employed"] / 365.25).mask(anom)  # NaN qalır
        out["ft_age_years"] = age
        out["ft_employed_years"] = emp
        out["ft_employed_age_ratio"] = _ratio(emp, age)
        out["ft_income_per_person"] = _ratio(d["amt_income_total"], d["cnt_fam_members"])
        ext = d[EXT]
        out["ft_ext_source_mean"] = ext.mean(axis=1)
        out["ft_ext_source_min"] = ext.min(axis=1)
        out["ft_ext_source_prod"] = ext.prod(axis=1, skipna=True).where(ext.notna().any(axis=1))
        out["ft_ext_source_missing_cnt"] = ext.isna().sum(axis=1).astype("int8")
        out["ft_doc_count"] = d[DOCS].sum(axis=1).astype("int8")
        req = d[REQ]
        out["ft_bureau_req_total_year"] = req.sum(axis=1).where(req.notna().any(axis=1))
        out["ft_days_registration_years"] = -d["days_registration"] / 365.25
        out["ft_id_publish_years"] = -d["days_id_publish"] / 365.25
        return out[FEATURE_NAMES].astype({c: "float64" for c in FEATURE_NAMES
                                          if c not in ("ft_ext_source_missing_cnt", "ft_doc_count")})
