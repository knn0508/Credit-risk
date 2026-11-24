# Fairness xülasəsi (biznes/hüquqi baxış üçün) — xgb-20261124-a9b6c81
Statistik audit, ədalətlilik sübutu deyil. Band payları OOF-da (246 008), hədlər fərziyyədir (low 0.0274 / medium 0.1915). Sistem qərar dəstəyidir.

| Qrup | Holdout defolt | Low | Medium | High | Kalibrasiya fərqi (holdout) |
|---|---|---|---|---|---|
| Qadın (F) | 7.0% | 32.5% | 59.0% | 8.5% | +0.005 |
| Kişi (M) | 10.2% | 25.1% | 62.0% | 12.9% | −0.009 |
| <30 | 11.3% | 15.0% | 67.1% | 17.9% | +0.001 |
| 30–39 | 9.6% | 24.4% | 62.1% | 13.5% | 0.000 |
| 40–49 | 7.6% | 31.6% | 59.6% | 8.8% | +0.001 |
| 50–59 | 6.4% | 37.8% | 56.7% | 5.5% | −0.002 |
| 60+ | 5.0% | 43.7% | 53.5% | 2.8% | +0.001 |

Oxunuş:
1. **Gender:** `code_gender` modeldə YOXDUR (decisions/0002), yalnız audit. Buna baxmayaraq kişilər High-a 1.5× tez düşür (12.9% vs 8.5%) — real defolt fərqini (10.2% vs 7.0%) proksilər vasitəsilə izləyir. Kişi qrupunda model riski ~0.9 faiz bəndi az qiymətləndirir, qadında ~0.5 bəndi çox.
2. **Yaş:** `days_birth` feature-dır. <30 qrupu 60+ ilə müqayisədə High-a ~6× çox düşür; defolt dərəcəsi fərqi 2.3× (11.3% vs 5.0%) — model fərqi defoltdan çox böyüdür. Kalibrasiya hər qrupda yaxşıdır, AUC 60+ üçün ən aşağıdır (0.748). Yaşa görə fərqli rəftarın hüquqi məqbulluğu yurisdiksiyadan asılıdır.
3. **Region:** region_rating 3 üçün High 17.6% (defolt 11.0%), rating 1 üçün 3.7% (4.7%) — sosial-coğrafi proksi ola bilər.
4. Kiçik qruplar (n<100) üçün AUC hesablanmayıb; peşə/təşkilat/ailə nəticələri reports/subgroups_*_holdout.md-dədir.

Qərar tələb edən suallar: (a) yaş feature-ı saxlanılsın, yoxsa çıxarılsın/məhdudlaşdırılsın (çıxarılsa performans itkisi 04 ilə ölçülməlidir)? (b) band payı yaş/gender üzrə hansı fərqlərə yol verilir? (c) Medium/High üçün insan baxışı prosesi.
