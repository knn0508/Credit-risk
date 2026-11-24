# 0002 — Qorunan atributlar (qaralama, Agent 01; insan təsdiqi gözlənilir)
- `code_gender` model feature-ı OLMAYACAQ. Yalnız 05-in subgroup fairness auditində istifadə olunur (processed data-da qalır, feature_names-də yox).
- Yaş (`days_birth`/`ft_age_years`) feature kimi QALIR (kredit riskində güclü və qanuni siqnal), amma 05 yaş qrupları üzrə audit edir; qrup üzrə sistematik pis nəticə çıxarsa 01-ə qaytarır.
- Digər həssas/proksi sahələr (family_status, region, occupation) 03 catalogue-da "proksi riski" ilə işarələnir, 05 audit edir.
- Bundle metadata-da `excluded_protected_features` siyahısı olur.
