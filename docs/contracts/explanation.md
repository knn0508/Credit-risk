# İzah kontraktı — QARALAMA v0.1
```json
{"method":"shap_tree|shap_linear","base_value":0.0,
 "top_positive_factors":[{"feature_name":"ext_source_2","display_name":"External score 2","value":0.31,"contribution":0.042}],
 "top_negative_factors":[{"feature_name":"...","display_name":"...","value":0,"contribution":-0.03}],
 "note":"SHAP model davranışını izah edir, səbəb-nəticə sübutu deyil."}
```
- `contribution`: SHAP dəyəri (log-odds və ya model çıxış fəzası; `metadata.explanation_space` ilə qeyd olunur). Müsbət = riski artırır.
- Hər siyahı default top 5, ardıcıllıq |contribution| azalan. `value` göstərilməsi konfiqurasiya olunur (həssaslıq üçün söndürülə bilər).
- `display_name`: `configs/feature_display_names.yaml` (03 doldurur, 05 istifadə edir); yoxdursa feature_name.
- Hesablama src/explainability (05); 06 yalnız göstərir. Fərdi izah loga yazılmır.
