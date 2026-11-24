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

## Data kontraktı v1.0-dan nəticələr (01 dondurdu)
- Baza defolt dərəcəsi train-də 8.073% (307 511 sətir) → PR-AUC baza xətti ≈0.081; band payı/lift bu dərəcəyə nisbətən hesablanır.
- Zaman sütunu yoxdur → zaman-əsaslı validation mümkün deyil; model card "Məhdudiyyətlər"də qeyd olunacaq (təsadüfi stratified split gələcək paylanma sürüşməsini ölçmür).
- Train/test paylanma sürüşməsi (|SMD|<0.5) məlumdur; hesabatda qeyd, test setdə metrik hesablanmır (TARGET yoxdur).
- Subgroup sütunları kiçik hərflə (`code_gender`, `name_education_type`, `name_family_status`, `days_birth`). `code_gender`
  'XNA'→NaN: audit-də ayrıca "unknown" qrupu; kiçik qruplar (n < 100 və ya <10 müsbət) üçün AUC hesablanmır, "insufficient" yazılır.
- `code_gender` model feature-ı deyil (decisions/0002); audit üçün processed datadan SK_ID_CURR ilə join edilir (join-dən əvvəl/sonra sətir sayı yoxlanır).
- Real data yoxlandı (2026-11-24): açar/target kiçik hərflidir (`sk_id_curr`, `target`). 01 kontraktı dəqiqləşdirdi: OOF və split.json da kiçik hərf (`sk_id_curr, fold, p_raw, target`) — normallaşdırma lazım deyil.
  `code_gender`: F 202 448, M 105 059, NaN 4 → "unknown" qrupu n<100 olduğu üçün "insufficient".

## Leakage yoxlaması (validation hesabatında)
- 03-ün `docs/features/eda-leakage-report.md` nəticəsi qəbul olunur (TARGET yoxdur, |AUC−0.5|>0.25 şübhəli feature yoxdur, gələcək-tarix yoxdur; 24 ft_ feature). Bu evristikdir: "müraciətdən sonra" aqreqat sətri data özündən sübut oluna bilməz.
- 05-in müstəqil əlavə yoxlaması: final modelin qlobal SHAP top-15 siyahısı məzmunca nəzərdən keçirilir (ext_source, kredit/mal məbləği, bureau/tarixçə); proqnoz anında məlum olmayan sahə varsa 01/03-ə qaytarılır.
- Hesabatda qeyd: OOF CV AUC (≈0.77–0.78) real kredit-skorinq üçün gözlənilən aralıqdadır; qeyri-adi yüksək dəyər olmadığı üçün leakage göstəricisi yoxdur.
