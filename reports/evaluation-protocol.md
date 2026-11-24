# Evaluation protokolu (Agent 05) — QARALAMA v0.1

Əsas: docs/decisions/0001, docs/contracts/model-bundle.md. Seed 42. application_test istifadə olunmur.

## Data bölgüsü (04 ilə razılaşdırılmalı)
1. application_train → stratified 80/20: `train` / `holdout` (04 yaradır, split indekslərini model metadata-da saxlayır).
2. `train` daxilində 5-fold stratified CV → **out-of-fold (OOF) ehtimallar** (04 verir).
3. **Kalibrasiya və band hədləri yalnız OOF üzərində seçilir** (holdout-da yox).
4. **Holdout yalnız bir dəfə**, son hesabat üçün: ROC-AUC, PR-AUC, Brier, calibration curve, confusion matrix, cost, subgroup.
   Holdout nəticəsinə baxıb hədd/model dəyişmək qadağandır (leakage).

## Kalibrasiya
- Metodlar: isotonic və Platt (sigmoid); OOF üzərində CV ilə müqayisə (Brier, ECE). Daha yaxşısı `calibrator.joblib`
  (`predict(p_raw) -> p_cal`).
- Hesabat: reliability diagram (10 quantile bin), Brier, ECE; kalibrasiyadan əvvəl/sonra.

## Risk bandı
- `band(p_cal)`: p ≤ low_max Low; ≤ medium_max Medium; əks halda High (`src/evaluation/risk_bands.py`).
- Hədlər OOF-da seçilir: hədəf — Low bandında default dərəcəsi portfel ortalamasından xeyli aşağı, High bandında xeyli yuxarı,
  hər band minimum ölçüdə (məs. ≥10% müşahidə). Variantlar cədvəli (hədd → band payı, band üzrə default dərəcəsi, lift) hesabatda.
- Nəticə `configs/risk_policy.yaml` üçün **təklif** (status: proposal); biznes təsdiqi olmadan "fərziyyə". 01 təsdiqləyir.

## Metrikalar
- Əsas: ROC-AUC, PR-AUC (baza xətti = müsbət nisbət). Accuracy əsas deyil.
- Confusion matrix: hər band-hədd variantı üçün (High = "müsbət" xəbərdarlıq kimi), precision/recall/lift.
- Cost matrix: FN/FP xərc nisbəti **fərziyyə** kimi etiketlənir (məs. FN:FP = 5:1, parametrik həssaslıq cədvəli 2:1…10:1). Real biznes xərci deyil.
- Bootstrap CI (1000, seed 42) AUC üçün.

## Subgroup / fairness audit
- Qruplar: code_gender, name_education_type, yaş qrupları (days_birth-dən), name_family_status.
- Hər qrup: say, default dərəcəsi, orta p_cal, AUC, High band payı, kalibrasiya fərqi.
- Qeyd: audit statistikdir, ədalətlilik sübutu deyil; həssas atributlar modeldə istifadəsi 01 ilə müzakirə (hüquqi/etik risk).

## Explainability
- SHAP TreeExplainer (ağac modellər) / LinearExplainer; global (mean|SHAP|) və lokal top-5 müsbət/mənfi (explanation.md).
- `explanation_space` (log-odds) metadata-da qeyd. SHAP model davranışıdır, səbəb-nəticə deyil. Fərdi izah loga yazılmır.

## Çıxışlar
`src/evaluation/{metrics,calibration,risk_bands,cost,subgroups}.py`, `src/explainability/shap_explainer.py`,
`reports/model_card.md`, `reports/validation_report.md`, `reports/figures/`, `configs/risk_policy.yaml` təklifi (01-ə handoff).
Testlər: metrik funksiyaları, band sərhədləri (≤ daxil), SHAP shape/ardıcıllıq.
