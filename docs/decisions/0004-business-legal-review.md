# 0004 — Biznes/hüquqi baxış nəticəsi (insan qərarı, 2026-11-25; Agent 01 qeyd edir)
Bu sənəd hüquqi məsləhət DEYİL; yurisdiksiya üzrə yekun rəy hüquqşünas tərəfindən verilməlidir.

## Qərarlar (insan tərəfindən seçilib)
1. **İstifadə:** yalnız demo/akademik prototip. Real kredit qərarı YOXDUR; real müştəri/müraciət datası ilə canlı istifadə YOXDUR.
2. **İstinad çərçivəsi:** Aİ (GDPR / AI Act). Kredit qiymətləndirməsi AI Act-də yüksək riskli kateqoriyadır; real istifadəyə keçilsə aşağıdakılar məcburidir.
3. **Yaş:** feature kimi saxlanılır, monitorinq olunur (decisions/0002 qüvvədə). Yaşı çıxarmaq band fərqini azaltmır (reports/fairness_age_ablation.md); performans itkisi kiçikdir.
4. **Band siyasəti:** hədlər (low 0.0274 / medium 0.1915) fərziyyə olaraq qalır; Low 30% / Medium 60% / High 10%. Bütün cavablarda "biznes təsdiqi yoxdur" xəbərdarlığı saxlanır.

## Prototip üçün tətbiq olunan qaydalar
- Hər cavab/UI: "Qərar dəstəyidir; avtomatik təsdiq/rədd deyil" + "Yalnız demo/prototip; real kredit qərarları üçün deyil".
- Model card-da (05): nəzərdə tutulan istifadə = demo; Aİ yüksək risk qeydi; məlum fairness fərqləri (yaş, gender-proksi, region).
- Yaş/gender/region band fərqləri açıq sənədləşir; "ədalətlilik sübutu" iddiası yoxdur.

## Real istifadədən ƏVVƏL məcburi (indi icra OLUNMAYIB)
- Hüquqşünas rəyi (Aİ/ölkə üzrə): AI Act yüksək risk tələbləri (risk idarəetməsi, data idarəetməsi, texniki sənəd, loglama, insan nəzarəti, dəqiqlik/davamlılıq), GDPR (hüquqi əsas, Maddə 22 avtomatlaşdırılmış qərar, DPIA, izah hüququ).
- Real xərc nisbəti (FN:FP) və biznes tutumu ilə hədlərin yenidən seçilməsi (05); biznes təsdiqi (risk_policy.business_approval).
- Yaş/region/gender fərqləri üçün hüquqi qiymətləndirmə; Medium/High üçün insan baxışı prosesi.
- Real data ilə monitorinq (drift, kalibrasiya, subgroup), model müddəti/yenidən validasiya planı.
- Data mənbəyi Kaggle Home Credit-dir: lisenziya/istifadə şərtləri real məqsəd üçün yoxlanmalıdır.
