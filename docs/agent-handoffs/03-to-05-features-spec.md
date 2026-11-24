# 03 -> 05: feature spec (v0.2)
- Catalogue: docs/features/feature-catalogue.md (ad, məntiq, null siyasəti). Kod: src/features (ApplicationFeatures 16 + AggregateFeatures 7 = 23 ft_), stateless -> fit leakage yoxdur.
- Leakage hesabatı: docs/features/eda-leakage-report.md (evristik; məhdudiyyət: mütləq tarix yoxdur).
- display_name: configs/feature_display_names.yaml (ft_ + əsas processed/aqreqat sütunlar; yoxdursa feature_name).
- Fairness (decisions/0002): code_gender modeldən çıxarılıb (src.features.EXCLUDED_PROTECTED_FEATURES), audit üçün processed-də var.
  Proksi ola biləcək: ft_age_years, cnt_children, name_family_status, region_*, organization_type, occupation_type, name_education_type.
  Yaş qalır -> sənin auditin.
- Izah üçün: ft_ratio feature-ları (ft_credit_term, ft_credit_goods_ratio, ft_ext_source_*) SHAP-da ən güclülərdir (04: ft_ext_source_mean #1). SHAP korrelyasiyalı feature-lar (ext_source_* və ft_ext_source_*) arasında təsiri bölür — izahda bunu qeyd et; səbəb-nəticə sübutu deyil.
- NaN: 23 ft_-dən ən çoxu ft_cc_* (72-81%), cc tarixçəsi olmayanlarda; xəta deyil.
