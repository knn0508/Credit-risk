"""Raw dataset inventory (stdlib only): rows, columns, null counts, key uniqueness.

Usage: python -m src.data.inventory [--config configs/data.yaml] [--out data/interim/inventory.json]
Reads every CSV in raw_dir once, streaming. Nothing is written to Git-tracked paths by default.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

# Columns whose uniqueness / null-ness we check per table (grain keys from the data contract).
KEYS = {
    "application_train": ["SK_ID_CURR"],
    "application_test": ["SK_ID_CURR"],
    "bureau": ["SK_ID_BUREAU"],
    "previous_application": ["SK_ID_PREV"],
}


def load_config(path):
    """Flat `key: value` config; uses PyYAML when installed, else a minimal parser."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        cfg = {}
        for line in text.splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" in line:
                k, v = line.split(":", 1)
                cfg[k.strip()] = v.strip()
        return cfg


def inventory_file(path, keys):
    # description file has a non-utf8-safe header on some mirrors; be tolerant
    with open(path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        header = next(reader)
        nulls = [0] * len(header)
        key_idx = [header.index(k) for k in keys if k in header]
        seen = [set() for _ in key_idx]
        rows = 0
        ragged = 0
        for row in reader:
            rows += 1
            if len(row) != len(header):
                ragged += 1
                continue
            for i, v in enumerate(row):
                if v == "":
                    nulls[i] += 1
            for s, i in zip(seen, key_idx):
                s.add(row[i])
    return {
        "rows": rows,
        "n_columns": len(header),
        "ragged_rows": ragged,
        "columns": {
            h: {"nulls": n, "null_pct": round(100 * n / rows, 3) if rows else None}
            for h, n in zip(header, nulls)
        },
        "key_unique": {header[i]: len(s) for i, s in zip(key_idx, seen)},
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/data.yaml")
    ap.add_argument("--out", default="data/interim/inventory.json")
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    raw = Path(cfg["raw_dir"])
    result = {}
    for p in sorted(raw.glob("*.csv")):
        if p.stem in ("sample_submission", "HomeCredit_columns_description"):
            continue
        print(f"[inventory] {p.name} ...", file=sys.stderr, flush=True)
        result[p.stem] = inventory_file(p, KEYS.get(p.stem, []))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"[inventory] wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
