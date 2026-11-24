"""Generate docs/data/data-dictionary.md from data/processed/schema.json + HomeCredit_columns_description.csv."""
import json
from pathlib import Path

import pandas as pd

from src.data.inventory import load_config


def main():
    cfg = load_config("configs/data.yaml")
    schema = json.loads((Path(cfg["processed_dir"]) / "schema.json").read_text(encoding="utf-8"))
    desc = pd.read_csv(Path(cfg["raw_dir"]) / "HomeCredit_columns_description.csv", encoding="latin-1")
    d = {(r.Table.split(".")[0], r.Row.strip().lower()): str(r.Description).replace("\n", " ").strip()
         for r in desc.itertuples()}
    app_desc = {k[1]: v for k, v in d.items() if k[0].startswith("application")}
    m = schema["meta"]
    out = ["# Data Dictionary (Agent 02, avtomatik: `python -m src.data.dictionary`)",
           f"Kontrakt: {m['contract_version']} · build: {m['built_at_utc']} · commit: {m['git_commit']} · "
           f"train {m['rows']['train']:,} / test {m['rows']['test']:,} sətir · {m['n_columns']} sütun (train).",
           "Grain: 1 sətir = 1 müraciət (`sk_id_curr`). `target` yalnız train-də. Tarixçəsizlik: `<mənbə>_has_history`=0, "
           "`*_count`/`*_nunique`=0, digər aqreqatlar NaN.", "",
           "## Application sütunları", "| sütun | dtype | null % | təsvir |", "|---|---|---|---|"]
    agg = []
    for c in schema["columns"]:
        if c["source_table"].startswith("application"):
            text = app_desc.get(c["column"], "bayraq: DAYS_EMPLOYED=365243 sentineli idi" if c["stat"] == "sentinel_flag" else "")
            out.append(f"| {c['column']} | {c['dtype']} | {c['null_pct_train']} | {text} |")
        else:
            agg.append(c)
    out += ["", "## Aqreqat sütunlar (SK_ID_CURR səviyyəsi)", "| sütun | dtype | null % | mənbə cədvəl | mənbə sütun | stat |", "|---|---|---|---|---|---|"]
    for c in agg:
        out.append(f"| {c['column']} | {c['dtype']} | {c['null_pct_train']} | {c['source_table']} | {c['source_column']} | {c['stat']} |")
    Path("docs/data/data-dictionary.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{len(schema['columns'])} columns documented")


if __name__ == "__main__":
    main()
