"""bank.db (SQLite) → Supabase Postgres `customers`. İşlət:  DATABASE_URL=postgresql://... python bank-website/db/seed_supabase.py
Təkrar işlədilə bilər: cədvəl silinib yenidən yaradılır. RLS açılır, policy yoxdur (yalnız server tərəfi birbaşa bağlantı)."""
import os
import sqlite3
from pathlib import Path

import psycopg

SRC = Path(__file__).resolve().parent / "bank.db"
PG_TYPE = {"INTEGER": "BIGINT", "REAL": "DOUBLE PRECISION", "TEXT": "TEXT"}
PIN_CHECK = "CHECK (pin ~ '^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{7}$')"  # Postgres regex lookahead dəstəkləyir


def main() -> None:
    lite = sqlite3.connect(SRC)
    info = lite.execute("PRAGMA table_info(customers)").fetchall()  # cid, name, type, notnull, default, pk
    cols = []
    for _, name, typ, notnull, _, pk in info:
        d = f'"{name}" {PG_TYPE[typ.upper()]}'
        if name == "pin":
            d += f" PRIMARY KEY {PIN_CHECK}"
        elif name == "sk_id_curr":
            d += " UNIQUE NOT NULL"
        elif notnull:
            d += " NOT NULL"
        cols.append(d)
    rows = lite.execute("SELECT * FROM customers").fetchall()
    names = ",".join(f'"{i[1]}"' for i in info)
    with psycopg.connect(os.environ["DATABASE_URL"], prepare_threshold=None) as con:
        con.execute("DROP TABLE IF EXISTS customers")
        con.execute(f"CREATE TABLE customers ({', '.join(cols)})")
        con.execute("ALTER TABLE customers ENABLE ROW LEVEL SECURITY")
        with con.cursor() as cur:
            cur.executemany(f"INSERT INTO customers ({names}) VALUES ({','.join(['%s'] * len(info))})", rows)
        n = con.execute("SELECT count(*) FROM customers").fetchone()[0]
    print(f"{n} customers -> Supabase")


if __name__ == "__main__":
    main()
