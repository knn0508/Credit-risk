# Brief 03 — Features
**Objective:** biznes mənalı feature-lar, leakage yoxsa. **Inputs:** 02-nin processed data + data dictionary.
**Scope:** notebooks/eda/, src/features/, feature catalogue. **Interface:** sklearn-uyğun transformer (fit yalnız train), train/inference eyni kod; feature adları ft_ prefiksi; configs/feature_display_names.yaml (display_name).
**Acceptance:** catalogue (ad, tip, null siyasəti, mənbə, məntiq); leakage yoxlama hesabatı. **Tests:** transformer fit/transform, null davranışı, sütun sırası stabil. **Handoff:** feature spec → 04, 05.
