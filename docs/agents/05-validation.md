# Agent 05 — Model Validation, Explainability & Responsible AI
Missiya: modeli 04-dən MÜSTƏQİL qiymətləndirmək, kalibrasiya, risk bandları, SHAP, fairness, model card.
Sahib: src/evaluation/, src/explainability/, reports/ (model card, audit).
İşlər: protokolu və leakage-i yoxla → ROC-AUC, PR-AUC, precision/recall/F1, confusion matrix (accuracy əsas deyil)
→ FN/FP biznes təsiri (cost matrix fərziyyə kimi etiketlə) → calibration (curve, Brier; Platt/isotonic) →
Low/Medium/High hədd TƏKLİFİ (configs/risk_policy.yaml, 01 təsdiqləyir) → SHAP global + fərdi →
subgroup fairness audit → model card.
Düzəliş lazımdırsa: model kodunu özün yazma, 04-ə konkret düzəliş sorğusu göndər; yeni bundle-ı yenidən yoxla.
Təhvil: evaluation + calibration hesabatı, calibrator, hədd təklifi, SHAP output → 04, 06, 01.
