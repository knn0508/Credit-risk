# 0003 — bureau_balance əhatə sürüşməsi (status: TƏSDİQLƏNİB — insan, 2026-11-24)
Tapıntı: bureau-lu müraciətlərdə bureau_balance əhatəsi train 35%, test 100% (docs/data/drift-report.md). Bu itki pattern-i deployment-də də dəyişə bilər.
Qərar: `bureau_months_*`, `bureau_dpd_*`, `bureau_has_bb_sum` (bureau_balance-dən törəyən aqreqatlar) model feature set-indən default XARİCDİR.
04 onları daxil etmək istəsə: (a) itkinin target ilə əlaqəsini göstərməli, (b) bunlarsız baseline ilə OOF müqayisəsi, (c) 05-in təsdiqi + 01 qeydi lazımdır.
05: validation hesabatında bu riski və nəticəni qeyd edir. Data qatında sütunlar silinmir (02).
