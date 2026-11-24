"""Skorlama məntiqi. Feature/preprocessing məntiqi təkrarlanmır: bundle-dakı model Pipeline-dır."""
import uuid
from datetime import datetime, timezone

import pandas as pd

from api.bundle import Bundle
from api.schemas import Prediction


def _band(p: float, policy: dict) -> str:
    # Qayda 05-in src/evaluation/risk_bands.py funksiyasındadır; burada özbaşına yazılmır.
    from src.evaluation.risk_bands import band
    return band(p, policy["low_max"], policy["medium_max"])


def _coerce(b: Bundle, df: pd.DataFrame) -> pd.DataFrame:
    """JSON null → object dtype problemini həll edir: tipləri background (train) dtype-larına gətirir.
    Rəqəm sütununa mətn gəlsə ValueError (→ 422)."""
    ref = b.ref_dtypes()
    for c in df.columns:
        t = ref.get(c)
        if t is not None and pd.api.types.is_numeric_dtype(t) and not pd.api.types.is_bool_dtype(t):
            df[c] = pd.to_numeric(df[c], errors="raise").astype("float64")
        elif t is not None and not pd.api.types.is_numeric_dtype(t):
            df[c] = df[c].astype(t)  # kateqorik: train dtype (null → NaN/NA)
        elif df[c].isna().all():
            df[c] = df[c].astype("float64")  # referans yoxdur, bütün-null: float NaN
    return df


def row_is_valid(b: Bundle, a: dict) -> bool:
    """DataFrame qurmadan ucuz yoxlama: background-a görə rəqəm sütunlarında rəqəm/null olmalıdır."""
    for c, t in b.ref_dtypes().items():
        v = a.get(c)
        if v is None or not pd.api.types.is_numeric_dtype(t) or pd.api.types.is_bool_dtype(t):
            continue
        try:
            float(v)
        except (ValueError, TypeError):
            return False
    return True


def _derived_names() -> list[str]:
    from src.features.aggregate_features import FEATURE_NAMES_B
    from src.features.application_features import FEATURE_NAMES
    return list(FEATURE_NAMES) + list(FEATURE_NAMES_B)


def _derive(b: Bundle, applicants: list[dict]) -> pd.DataFrame:
    """ft_* feature-ları train ilə EYNİ src/features kodundan (stateless) hesablayır; yalnız bundle-ın istədikləri.
    Sorğuda artıq verilmiş ft_* dəyəri üstünlük təşkil edir. Çatışan xam giriş → NaN (train davranışı)."""
    from src.features import AggregateFeatures, ApplicationFeatures
    want = [f for f in _derived_names() if f in set(b.feature_names)]
    if not want:
        return pd.DataFrame(index=range(len(applicants)))
    cols = sorted({k for a in applicants for k in a} | set(b.feature_names))
    raw = pd.DataFrame([{c: a.get(c) for c in cols} for a in applicants], columns=cols)
    # transformerlərin oxuduğu xam sütunlar (çatışanlar NaN); rəqəm olmayan dəyər → ValueError (→ 422)
    from src.features.application_features import DOCS, EXT, REQ
    need = set(EXT) | set(DOCS) | set(REQ) | {
        "amt_credit", "amt_income_total", "amt_annuity", "amt_goods_price", "days_birth", "days_employed",
        "days_registration", "days_id_publish", "cnt_fam_members",
        "bureau_amt_credit_sum_debt_sum", "bureau_amt_credit_sum_sum", "bureau_amt_credit_sum_overdue_sum",
        "previous_application_amt_credit_mean", "previous_application_amt_application_mean",
        "previous_application_amt_credit_max", "credit_card_balance_amt_balance_mean",
        "credit_card_balance_amt_credit_limit_actual_mean", "credit_card_balance_amt_payment_current_mean",
        "installments_payments_amt_payment_sum", "installments_payments_amt_instalment_sum"}
    for c in need:
        raw[c] = pd.to_numeric(raw[c], errors="raise").astype("float64") if c in raw else float("nan")
    ft = pd.concat([ApplicationFeatures().fit(raw).transform(raw), AggregateFeatures().fit(raw).transform(raw)], axis=1)
    return ft[want]


def to_frame(b: Bundle, applicants: list[dict]) -> tuple[pd.DataFrame, list[list[str]]]:
    """Sütunları feature_names sırasına salır; çatışan → NaN+warning, naməlum → ignore+warning.
    Törəmə ft_* sorğuda yoxdursa avtomatik hesablanır (xəbərdarlıq sayı ayrıca)."""
    known = set(b.feature_names)
    derived = set(_derived_names()) & known
    ft = _derive(b, applicants)
    rows, warns = [], []
    for n, a in enumerate(applicants):
        w = []
        auto = [f for f in b.feature_names if f in derived and a.get(f) is None]
        missing = [f for f in b.feature_names if f not in a and f not in derived]
        unknown = [k for k in a if k not in known and k != "SK_ID_CURR"]
        if missing:
            w.append(f"{len(missing)} çatışmayan sahə null qəbul edildi")
        if unknown:
            w.append(f"{len(unknown)} naməlum sahə nəzərə alınmadı")
        if auto:
            w.append(f"{len(auto)} törəmə (ft_) feature avtomatik hesablandı")
        row = {f: a.get(f) for f in b.feature_names}
        for f in auto:
            row[f] = ft.iloc[n][f]
        rows.append(row)
        warns.append(w)
    return _coerce(b, pd.DataFrame(rows, columns=b.feature_names)), warns


def score(b: Bundle, applicants: list[dict]) -> list[Prediction]:
    X, warns = to_frame(b, applicants)
    p = b.model.predict_proba(X)[:, 1]
    calibrated = b.use_calibrator
    if calibrated:
        p = b.calibrator.predict(p)
    now = datetime.now(timezone.utc).isoformat()
    out = []
    for pi, w in zip(p, warns):
        w = list(w) + b.warnings
        if not calibrated:
            w.append("calibrator tətbiq olunmur (yoxdur və ya metadata.calibrated!=true): xam ehtimal istifadə olunur")
        if b.dev_mode:
            w.append("DEV rejimi: bundle təsdiqlənməyib")
        out.append(Prediction(
            prediction_id=str(uuid.uuid4()), timestamp=now,
            model_version=b.metadata["model_version"],
            prediction_probability=float(pi), risk_band=_band(float(pi), b.risk_policy),
            calibrated=calibrated, warnings=w))
    return out
