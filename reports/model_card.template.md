# Model card — <MODEL_VERSION>  (ŞABLON: final bundle gələndə doldurulur)
Status: <unvalidated|validated|approved> · Hesabat tarixi: <YYYY-MM-DD> · Seed 42 · data_version: <hash>

## Məqsəd və istifadə
Home Credit kredit müraciətləri üçün defolt ehtimalı və Low/Medium/High risk bandı. **Qərar dəstəyidir; avtomatik təsdiq/rədd yoxdur.**
Nəzərdə tutulmayan istifadə: avtomatik qərar, Home Credit-dən kənar populyasiya, həssas atributla birbaşa qərar.

## Data və protokol
application_train 307 511 sətir (defolt 8.073%). Stratified 80/20 train/holdout; train-də 5-fold CV (OOF). Kalibrasiya və hədlər yalnız OOF-da;
holdout yalnız son hesabatda, bir dəfə. application_test istifadə olunmayıb. Model: <alg>, feature sayı <n>, `code_gender` feature deyil (decisions/0002).

## Performans (holdout, son hesabat)
ROC-AUC <> (CI <>) · PR-AUC <> (baza 0.081) · Brier <> · ECE <> · OOF CV ROC-AUC <> (fold std <>)

## Kalibrasiya və risk bandı
Metod: <isotonic|platt>. Hədlər: low_max <>, medium_max <> (**fərziyyə, biznes təsdiqi yoxdur**).
| Band | Pay | Defolt dərəcəsi | Lift |
|---|---|---|---|
Qeyd: band payları (Low ~<>%, High ~<>%) biznes tutumu ilə uzlaşdırılmalıdır (01 qeydi).

## İzahlılıq
SHAP (<method>), `explanation_space: log_odds`, xam model (kalibrasiyadan əvvəl). Qlobal top-15: <>. ext_source_* və ft_ext_source_*
korrelyasiyalıdır, təsir bölünür. SHAP model davranışıdır, səbəb-nəticə sübutu deyil. Müstəqil leakage baxışı: <nəticə>.

## Fairness audit (statistik)
Qruplar: gender, yaş, təhsil, ailə, peşə, təşkilat, region, uşaq sayı (reports/subgroups_*.md). Nəticə: <>. Yaş modeldə qalır (qanuni risk siqnalı), fərqlər <>.

## Məhdudiyyətlər
- Zaman sütunu yoxdur: zaman-əsaslı validation mümkün deyil, təsadüfi split gələcək sürüşməni ölçmür.
- Train/test paylanma sürüşməsi (|SMD|<0.5) məlumdur.
- Cost matrix FN:FP nisbətləri fərziyyədir, real biznes xərci deyil.
- Hədlər biznes təsdiqi olmadan fərziyyədir; model dəyişsə yenidən seçilməlidir.
- Audit proksi atributları tam aradan qaldırmır; ədalətlilik sübutu deyil.
