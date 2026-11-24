# İzah kontraktı — QARALAMA v0.1
```json
{"method":"shap_tree|shap_linear","explanation_space":"log_odds","base_value":0.0,
 "top_positive_factors":[{"feature_name":"ext_source_2","display_name":"External score 2","value":0.31,"contribution":0.042}],
 "top_negative_factors":[{"feature_name":"...","display_name":"...","value":0,"contribution":-0.03}],
 "note":"SHAP model davranışını izah edir, səbəb-nəticə sübutu deyil."}
```
- `contribution`: SHAP dəyəri, `explanation_space` sahəsi cavabda və metadata-da olur: `"log_odds"` (default; LightGBM/LogReg) və ya `"probability"`. Müsbət = riski artırır.
- Hər siyahı default top 5, ardıcıllıq |contribution| azalan. `value` default QAYTARILMIR; yalnız `include_values=true` ilə (bax prediction-api.md v0.2).
- `display_name`: `configs/feature_display_names.yaml` (03 doldurur, 05 istifadə edir); yoxdursa feature_name.
- Hesablama src/explainability (05); 06 yalnız göstərir. Fərdi izah loga yazılmır.
