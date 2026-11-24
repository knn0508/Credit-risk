# bureau_balance əhatə sürüşməsi — 05 müstəqil yoxlama (decisions/0003)
Status: ilkin yoxlama; final bundle gələndə təkrarlanacaq və validation_report-a daxil ediləcək.

## Sübut (application_train, bureau_has_history=1, n=263 491)
| bureau_balance aqreqatı | n | default dərəcəsi |
|---|---|---|
| var (bureau_months_count_sum notna) | 92 231 (35%) | 8.14% |
| yox (NaN) | 171 260 (65%) | 7.51% |
| bureau tarixçəsi ümumiyyətlə yox | 44 020 | 10.12% |

- İtkinin target ilə əlaqəsi zəifdir (0.6 faiz bəndi), amma sıfır deyil: model NaN-ı "bureau_balance yoxdur" siqnalı kimi öyrənə bilər. Test-də bu siqnal 100% "var" olduğundan train-də öyrənilən nümunə ötürülməz.
- Mövcud benchmark bundle `lgbm-20261124-66653dd` feature_names-ində `bureau_has_bb_sum`, `bureau_months_*`, `bureau_dpd_*` HƏLƏ VAR (0003-dən əvvəl qurulub). Aparıcı bundle-da olmamalıdır.

## Növbəti addımlar (aparıcı bundle gələndə)
1. feature_names-də bu 9 sütunun olmadığını yoxla (olarsa 04-ə düzəliş sorğusu).
2. Qismən: bb-siz vs bb-li OOF müqayisəsi yalnız 04 daxil etmək istəsə tələb olunur.
3. Validation hesabatında risk kimi qeyd: test/istehsal paylanması train-dən fərqli ola bilər; holdout (train-dən) bu sürüşməni əks etdirmir.
