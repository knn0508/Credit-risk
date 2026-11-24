# Model card — xgb-20261124-a9b6c81
Status: approved (texniki; yalnız DEMO/PROTOTİP; risk_policy approved_provisional, biznes təsdiqi YOXDUR) · Hesabat tarixi: 2026-11-24 · Seed 42 · data_version: 3f3e26a7c9e1fee9

## Məqsəd və istifadə
Home Credit kredit müraciətləri üçün defolt ehtimalı və Low/Medium/High risk bandı. **Qərar dəstəyidir; avtomatik təsdiq/rədd yoxdur.**
**Nəzərdə tutulan istifadə (decisions/0004): yalnız demo/akademik prototip.** Real kredit qərarı və real müştəri datası ilə canlı istifadə YOXDUR. Hər cavab/UI-da: "Qərar dəstəyidir; avtomatik təsdiq/rədd deyil" və "Yalnız demo/prototip; real kredit qərarları üçün deyil".
Nəzərdə tutulmayan istifadə: avtomatik qərar, Home Credit-dən kənar populyasiya, həssas atributla birbaşa qərar, real kredit qərarı.

## Tənzimləmə qeydi (Aİ)
İstinad çərçivəsi Aİ (GDPR / AI Act). Kredit qiymətləndirməsi AI Act-də **yüksək riskli** kateqoriyadır; bu sənəd hüquqi məsləhət deyil. Real istifadədən ƏVVƏL məcburi (indi icra OLUNMAYIB, bax docs/decisions/0004-*.md):
hüquqşünas rəyi (AI Act yüksək risk tələbləri, GDPR hüquqi əsas/Maddə 22/DPIA/izah hüququ); real FN:FP xərci və biznes tutumu ilə hədlərin yenidən seçilməsi və biznes təsdiqi;
yaş/region/gender fərqlərinin hüquqi qiymətləndirməsi və Medium/High üçün insan baxışı; real data ilə monitorinq (drift, kalibrasiya, subgroup) və yenidən validasiya planı; Kaggle Home Credit lisenziya şərtlərinin yoxlanması.

## Data və protokol
application_train 307 511 sətir (defolt 8.073%). Stratified 80/20 train (246 008) / holdout (61 503); train-də 5-fold CV (OOF). Kalibrasiya və hədlər yalnız OOF-da;
holdout yalnız son hesabatda, bir dəfə. application_test istifadə olunmayıb. Model: XGBoost (tuned, 10 cəhdlik random search, yalnız train CV), 242 feature
(processed + 23 ft_). `code_gender` feature deyil (decisions/0002); 9 bureau_balance törəməsi xaric (decisions/0003).

## Performans (holdout, son hesabat)
ROC-AUC 0.790 (CI 0.783–0.797) · PR-AUC 0.290 (baza 0.081) · Brier 0.0655 · ECE 0.0021 · OOF CV ROC-AUC 0.787, PR-AUC 0.277 (fold std ~0.001).
High=müsbət: precision 0.308, recall 0.377.

## Kalibrasiya və risk bandı
Metod: Platt (OOF-da fit). Hədlər: low_max 0.0274, medium_max 0.1915 (**fərziyyə, biznes təsdiqi yoxdur**).
| Band | Pay (holdout) | Defolt dərəcəsi | Lift |
|---|---|---|---|
| Low | 30.0% | 1.53% | 0.19 |
| Medium | 60.1% | 7.60% | 0.94 |
| High | 9.9% | 30.8% | 3.81 |
Qeyd: band payları (Low ~30%, High ~10%) biznes tutumu ilə uzlaşdırılmalıdır (01 qeydi).

## İzahlılıq
SHAP (shap_tree), `explanation_space: log_odds`, xam model (kalibrasiyadan əvvəl). Qlobal top-15 (orta |SHAP|): ft_ext_source_mean, ext_source_1, ft_ext_source_min,
ft_credit_term, amt_annuity, ft_credit_goods_ratio, ext_source_2, ft_ext_source_prod, ext_source_3, name_education_type, installments_payments_amt_payment_sum,
installments_payments_is_late_mean, ft_bureau_debt_credit_ratio, pos_cash_balance_cnt_instalment_future_mean, own_car_age. ext_source_* və ft_ext_source_*
korrelyasiyalıdır, təsir bölünür. SHAP model davranışıdır, səbəb-nəticə sübutu deyil. Müstəqil leakage baxışı: şübhəli dominant feature yoxdur.

## Fairness audit (statistik)
Qruplar: gender, yaş, təhsil, ailə, peşə, təşkilat, region, uşaq sayı (reports/subgroups_xgb-20261124-a9b6c81_{oof,holdout}.md). Xülasə: reports/fairness_summary_xgb-20261124-a9b6c81.md.
Nəticə: kalibrasiya bütün əsas qruplarda yaxşıdır; band payları real defolt fərqlərini izləyir. Yaş modeldə qalır (qanuni risk siqnalı, decisions/0002), fərqlər
(<30: High 17.9% vs 60+: 2.8%) defolt dərəcələri ilə uyğundur, lakin biznes/hüquqi baxış tələb edir. Yaşı (days_birth, ft_age_years, ft_employed_age_ratio) çıxarmaq band fərqini azaltmır (reports/fairness_age_ablation.md; proksilər saxlayır), performans itkisi kiçikdir (AUC −0.0018) → yaş saxlanılır və monitorinq olunur (decisions/0002, 0004).
**Məlum fərqlər:** yaş (<30 vs 60+ High ~6.5×, defolt fərqi 2.3×), gender-proksi (M High 12.9% vs F 8.5%, `code_gender` modeldə olmadan), region (rating 3 High 17.6% vs rating 1 3.7%). Ədalətlilik sübutu iddia edilmir.

## Məhdudiyyətlər
- Zaman sütunu yoxdur: zaman-əsaslı validation mümkün deyil, təsadüfi split gələcək sürüşməni ölçmür.
- Train/test paylanma sürüşməsi məlumdur (docs/data/drift-report.md); bureau_balance əhatə sürüşməsi (train 35% / test 100%) səbəbindən 9 sütun xaric edilib, holdout bu sürüşməni əks etdirmir.
- Cost matrix FN:FP nisbətləri fərziyyədir, real biznes xərci deyil.
- Hədlər biznes təsdiqi olmadan fərziyyədir; model dəyişsə yenidən seçilməlidir.
- Seçim 10 tuning cəhdi içindən OOF-da edilib; OOF bir qədər optimistik, holdout qərarlı rəqəmdir.
- Audit proksi atributları tam aradan qaldırmır; ədalətlilik sübutu deyil.
