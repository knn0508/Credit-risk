"""Demo bank DB: 100 müştəri, 7-simvollu PIN (A-Z0-9, ən azı 1 hərf + 1 rəqəm) + bütün processed feature-lar.

Mənbə: data/processed/application_test.parquet (target-siz; model/hədd seçimində istifadə olunmur).
Deterministikdir (seed). İşlət:  python bank-website/db/build_db.py
"""
import random
import sqlite3
import string
from pathlib import Path

import numpy as np
import pandas as pd

SEED, N = 42, 100
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "data" / "processed" / "application_test.parquet"
OUT = Path(__file__).resolve().parent / "bank.db"

FIRST_F = ["Aysel", "Leyla", "Nigar", "Səbinə", "Günay", "Nərmin", "Aytən", "Röya", "Fidan", "Sevinc", "Lamiyə", "Ülviyyə"]
FIRST_M = ["Elvin", "Rəşad", "Orxan", "Tural", "Kamran", "Murad", "Samir", "Vüqar", "Rauf", "Emin", "Cavid", "Nicat"]
LAST = ["Məmmədov", "Əliyev", "Hüseynov", "Quliyev", "Hacıyev", "Nəsirov", "Rzayev", "Səfərov", "Babayev", "İsmayılov"]
ALPHABET = string.ascii_uppercase + string.digits


def make_pins(n: int, rng: random.Random) -> list[str]:
    pins: set[str] = set()
    while len(pins) < n:
        p = "".join(rng.choice(ALPHABET) for _ in range(7))
        if any(c.isalpha() for c in p) and any(c.isdigit() for c in p):
            pins.add(p)
    return sorted(pins, key=lambda _: rng.random())


def sql_type(s: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(s):
        return "INTEGER"
    if pd.api.types.is_float_dtype(s):
        return "REAL"
    return "TEXT"


def main() -> None:
    rng = random.Random(SEED)
    df = pd.read_parquet(SRC).sample(N, random_state=SEED).reset_index(drop=True)
    assert "target" not in df.columns and df.sk_id_curr.is_unique

    pins = make_pins(N, rng)
    names = [
        (rng.choice(FIRST_F if g == "F" else FIRST_M), rng.choice(LAST) + ("a" if g == "F" else ""))
        for g in df["code_gender"]
    ]
    prof = pd.DataFrame({"pin": pins, "first_name": [a for a, _ in names], "last_name": [b for _, b in names]})
    data = pd.concat([prof, df], axis=1)

    OUT.unlink(missing_ok=True)
    cols = ["pin TEXT PRIMARY KEY CHECK (length(pin)=7 AND pin=upper(pin) AND pin GLOB '*[A-Z]*' AND pin GLOB '*[0-9]*' AND pin NOT GLOB '*[^A-Z0-9]*')",
            "first_name TEXT NOT NULL", "last_name TEXT NOT NULL"]
    cols += [f'"{c}" {sql_type(df[c])}' + (" UNIQUE NOT NULL" if c == "sk_id_curr" else "") for c in df.columns]
    con = sqlite3.connect(OUT)
    con.execute(f"CREATE TABLE customers ({', '.join(cols)})")
    obj = data.astype(object).where(data.notna(), None)  # NaN → NULL
    ph = ",".join("?" * data.shape[1])
    con.executemany(f"INSERT INTO customers VALUES ({ph})",
                    [tuple(v.item() if isinstance(v, np.generic) else v for v in r) for r in obj.itertuples(index=False)])
    con.commit()
    n, = con.execute("SELECT count(*) FROM customers").fetchone()
    print(f"{n} customers, {data.shape[1]} columns -> {OUT}")
    con.close()


if __name__ == "__main__":
    main()
