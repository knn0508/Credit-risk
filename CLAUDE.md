# Intelligent Credit Risk Assessment Platform — ortaq qaydalar

Dataset: Kaggle Home Credit Default Risk. 1 sətir = 1 kredit müraciəti (SK_ID_CURR).
TARGET yalnız application_train-də var. application_test target-sizdir və model/threshold
seçimində İSTİFADƏ EDİLMİR. Risk bandı (Low/Medium/High) kalibrasiya olunmuş ehtimaldan
və validation-da seçilən hədlərdən törədilir. Sistem qərar DƏSTƏYİDİR: avtomatik təsdiq/rədd yoxdur.

## Dataset sənədləri (həqiqət mənbəyi)
- Cədvəllərin təsviri: `docs/data/dataset-description.md`
- Cədvəl əlaqələri diaqramı: `docs/data/dataset-diagram.png`
- Sütun təsvirləri: `data/raw/HomeCredit_columns_description.csv`
Cədvəl əlaqələri və grain barədə yaddaşa yox, bu fayllara əsaslan. Faktiki sətir sayı, tip və null faizləri
yalnız real fayllardan (Agent 02 auditi) götürülür.

## Cədvəl əlaqələri (qısa)
- application_train/test: 1 sətir = 1 müraciət, açar SK_ID_CURR (TARGET yalnız train-də).
- bureau: SK_ID_CURR ilə bağlanır (1 müştəri → çox kredit). bureau_balance: SK_ID_BUREAU ilə bureau-ya (aylıq sətirlər).
- previous_application: SK_ID_CURR ilə bağlanır. POS_CASH_balance, installments_payments, credit_card_balance:
  SK_ID_PREV ilə previous_application-a bağlanır və SK_ID_CURR sütununu da saxlayır (aylıq/ödəniş sətirləri).
- Hamısı one-to-many-dir: əsas cədvələ birbaşa join etmə, əvvəl SK_ID_CURR səviyyəsinə aqreqasiya et.

## Agentlər, sahiblik, worktree
| # | Rol | Sahib olduğu yollar | Branch / worktree |
|---|-----|---------------------|-------------------|
| 01 | Orchestrator & Architect | CLAUDE.md, docs/architecture, docs/contracts, docs/decisions, configs/, inteqrasiya | agent/01-orchestrator · wt/01-orchestrator |
| 02 | Data Engineering & Quality | src/data/, data schemas, data testləri | agent/02-data · wt/02-data |
| 03 | EDA & Feature Engineering | notebooks/eda/, src/features/, feature catalogue + testlər | agent/03-features · wt/03-features |
| 04 | ML Modeling | src/models/, training configs, model metadata + testlər | agent/04-modeling · wt/04-modeling |
| 05 | Validation & Explainability | src/evaluation/, src/explainability/, reports/ | agent/05-validation · wt/05-validation |
| 06 | Backend, MLOps, UI | api/, app/, deployment/, Docker, integration testlər | agent/06-product · wt/06-product |

Rol təfərrüatı: `docs/agents/NN-*.md`. Öz sahibliyindən kənar faylı dəyişmə — Agent 01-ə kontrakt
dəyişikliyi sorğusu və ya sahib agentə mesaj göndər.

## İş qaydası (git worktree)
- Hər agent YALNIZ öz worktree-sində, öz branch-ında işləyir. `main`-ə birbaşa commit yoxdur.
- Commit mesajı prefiksi: `[02] ...`. Kiçik, tez-tez commit.
- Başlamazdan əvvəl və başqasının nəticəsi lazım olanda: `scripts/agents/sync.sh` (main-i branch-ına merge edir).
- Hazır iş main-ə yalnız Agent 01 / insan tərəfindən `scripts/agents/integrate.sh agent/NN-xxx` ilə daxil edilir.
- Python mühiti ortaqdır: `source ../../.venv/bin/activate`. Asılılıq əlavə etmək = Agent 01-ə sorğu (requirements.txt onun).
- `data/`, `artifacts/`, `.agents/` — ortaq symlink-lərdir, Git-ə girmir. Raw data, .env, secret, böyük model fayllarını commit etmə.

## Agentlərarası əlaqə
- Status lövhəsi: `.agents/TASKS.md` (öz sətrini yenilə). Log: `.agents/log.md`.
- Mesaj göndər: `scripts/agents/msg.sh <sənin_nömrən> <hədəf_nömrə> "mesaj"` (inbox-a yazır və hədəf agentin tmux pəncərəsinə xəbər verir).
- Öz gələn qutun: `.agents/inbox-NN.md` — hər işə başlamazdan əvvəl oxu.
- Böyük təhvillər üçün `docs/agent-handoffs/NN-to-MM-<mövzu>.md` yaz, mesajda ona istinad et.
- Təhvili qəbul edən agent yoxlayır; uyğun gəlmirsə konkret dəyişiklik sorğusu qaytarır.

## Standart status hesabatı
DONE: ... / FILES: ... / TESTS: ... / CONTRACTS: ... / BLOCKERS: ... / HANDOFF: ...
Test işlətmədən "tamamlandı" demə; işlənməyən testi açıq yaz.

## Sərt qaydalar
- Data leakage yoxdur: proqnoz anında məlum olmayan məlumat feature olmaz; fit yalnız train fold-da.
- Join-dən əvvəl/sonra sətir sayı və unikal SK_ID_CURR yoxlanır (one-to-many → əvvəl SK_ID_CURR-ə aqreqasiya).
- Train və inference eyni feature/preprocessing kodundan istifadə edir. Seed, config, model və data versiyası qeyd olunur.
- SHAP model davranışını izah edir, səbəb-nəticə sübutu deyil. Loglarda həssas müraciət məlumatı olmasın.
- Mövcud kodu oxumadan yeni struktur yaratma; əlaqəsiz fayllara toxunma.
