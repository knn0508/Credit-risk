# Yaş ablasiyası — fairness müqayisəsi (OOF, holdout-a toxunulmayıb)
Yaşlı: xgb-20261124-a9b6c81 (approved). Yaşsız: xgb-noage-20261124-0e2738c (days_birth + ft_age_years çıxarılıb, parametrlər eyni, yenidən tuning yox; unvalidated).
Hər model öz OOF-Platt kalibrasiyası və öz hədləri ilə (yaşlı 0.0274/0.1915, yaşsız 0.0278/0.1912 — praktik eynidir). n=246 008. Statistik audit, sübut deyil.

OOF: ROC-AUC 0.7869 → 0.7851 (−0.0018), PR-AUC 0.2768 → 0.2739 (−0.0029) (04 ölçməsi).

| Yaş qrupu | Defolt | High (yaşlı) | High (yaşsız) | Low (yaşlı) | Low (yaşsız) | calib gap (yaşlı) | calib gap (yaşsız) | AUC yaşlı / yaşsız |
|---|---|---|---|---|---|---|---|---|
| <30 | 11.5% | 17.9% | 19.8% | 15.1% | 13.8% | +0.0003 | +0.0064 | 0.760 / 0.758 |
| 30–39 | 9.6% | 13.5% | 12.4% | 24.4% | 25.3% | −0.0006 | −0.0045 | 0.788 / 0.787 |
| 40–49 | 7.7% | 8.9% | 8.4% | 31.6% | 32.1% | −0.0002 | −0.0019 | 0.790 / 0.789 |
| 50–59 | 6.1% | 5.5% | 6.1% | 37.8% | 35.8% | +0.0007 | +0.0039 | 0.778 / 0.776 |
| 60+ | 4.9% | 2.8% | 2.7% | 43.7% | 45.9% | 0.0000 | −0.0012 | 0.742 / 0.740 |

Gender (High): F 8.5% / 8.5%, M 12.9% / 12.9% — dəyişməyib.

## Nəticə
1. **Yaşı çıxarmaq band fərqini azaltmır.** <30 vs 60+ High nisbəti ~6.5× (yaşlı) → ~7.3× (yaşsız); <30 qrupunun High payı hətta 17.9% → 19.8%-ə artır. Real defolt fərqi cəmi 2.3×-dir, yəni model fərqi yenə böyüdür.
2. **Proksilər yaşı daşıyır.** Qalan feature-lar (ext_source_*, ft_employed_age_ratio — yaşdan törəmədir və çıxarılmayıb, days_employed, təhsil/peşə/ailə statusu və s.) yaş siqnalını bərpa edir. Yaşın birbaşa çıxarılması ədalətlilik baxımından səmərəsizdir.
3. **Kalibrasiya yaşsız variantda bir qədər pisləşir** (<30 qrupu +0.0064 az-qiymətləndirmə əvəzinə çox-qiymətləndirmə, 50–59 +0.0039), AUC itkisi kiçikdir, PR itkisi bir qədər aydındır.
4. Yaşsız variant ft_employed_age_ratio ilə birlikdə: OOF 0.7853/0.2744 (04), yəni fərq yoxdur — proksi təsirini yoxlamaq üçün 04 onu da çıxarıb bundle yarada bilər (bu hesabatda ölçülməyib).

## Tövsiyə (qərar 01/insan)
- decisions/0002 üçün: yaşı saxlamaq performansı bir qədər yaxşılaşdırır, çıxarmaq fərqi azaltmır → çıxarmağın fairness faydası yoxdur. Qalan risk band payı fərqinin biznes/hüquqi məqbulluğudur (limit və ya insan baxışı).
- Real azaldıcı variantlar (yaş-proksi feature-ların çıxarılması, qrup üzrə hədd, fairness məhdudiyyətli training) ayrı qərar və 04 işi tələb edir; qrup üzrə hədd ayrıca hüquqi baxış tələb edir.
- Holdout noage bundle üçün işlədilməyib; seçim edilsə, hədlər dondurulduqdan sonra işlədilər.
