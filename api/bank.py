"""Demo bank: PIN ilə müştəri sətirini DB-dən tapır / yeni müraciətçini DB-yə yazır. Yalnız demo."""
import os
import re
import sqlite3
from datetime import date
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

PIN_RE = re.compile(r"(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{7}")
_NON_FEATURE = ("pin", "first_name", "last_name")
_PROFILE = ("first_name", "last_name", "amt_income_total", "amt_credit", "amt_annuity", "name_contract_type")
DB_PATH = Path(os.environ.get("BANK_DB", Path(__file__).resolve().parents[1] / "bank-website" / "db" / "bank.db"))
# DATABASE_URL (Supabase Postgres) təyin olunubsa o istifadə olunur; yoxdursa lokal SQLite (dev).
DATABASE_URL = os.environ.get("DATABASE_URL")


def _pg():
    import psycopg
    from psycopg.rows import dict_row
    # prepare_threshold=None: Supabase pooler (transaction mode) prepared statement dəstəkləmir
    return psycopg.connect(DATABASE_URL, row_factory=dict_row, prepare_threshold=None)


def valid_pin(pin: str) -> bool:
    return PIN_RE.fullmatch(pin) is not None


def find_customer(pin: str) -> tuple[dict, dict] | None:
    """(profil, applicant-feature-lər) və ya None."""
    if DATABASE_URL:
        with _pg() as con:
            row = con.execute("SELECT * FROM customers WHERE pin = %s", (pin,)).fetchone()
    else:
        if not DB_PATH.exists():
            return None
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        try:
            row = con.execute("SELECT * FROM customers WHERE pin = ?", (pin,)).fetchone()
        finally:
            con.close()
    if row is None:
        return None
    r = dict(row)
    return {k: r[k] for k in _PROFILE}, {k: v for k, v in r.items() if k not in _NON_FEATURE}


class Application(BaseModel):
    """Yeni müraciətçinin özü haqqında verdiyi məlumat. Dəyərlər dataset-in kateqoriyaları ilə eynidir."""
    pin: str
    first_name: str = Field(min_length=1, max_length=40)
    last_name: str = Field(min_length=1, max_length=40)
    birth_date: date
    name_contract_type: Literal["Cash loans", "Revolving loans"]
    amt_credit: float = Field(gt=0, le=1e8)
    term_months: int = Field(ge=6, le=360)
    amt_income_total: float = Field(gt=0, le=1e8)
    name_income_type: Literal["Working", "Commercial associate", "State servant", "Businessman", "Pensioner",
                              "Student", "Unemployed", "Maternity leave"]
    employed_years: float = Field(ge=0, le=60)
    name_education_type: Literal["Secondary / secondary special", "Higher education", "Incomplete higher",
                                 "Lower secondary", "Academic degree"]
    name_family_status: Literal["Single / not married", "Married", "Civil marriage", "Separated", "Widow"]
    name_housing_type: Literal["House / apartment", "With parents", "Rented apartment", "Municipal apartment",
                               "Co-op apartment", "Office apartment"]
    cnt_children: int = Field(ge=0, le=15)
    flag_own_car: Literal["Y", "N"]
    flag_own_realty: Literal["Y", "N"]
    region_rating_client: Literal[1, 2, 3]
    has_work_phone: bool
    has_mobile_phone: bool
    has_email: bool
    amt_goods_price: Optional[float] = Field(default=None, gt=0, le=1e8)


class PinTaken(Exception):
    pass


def create_customer(a: Application) -> tuple[dict, dict]:
    """Müraciətçini DB-yə yazır (commit) və (profil, applicant) qaytarır. Skorlamadan ƏVVƏL çağırılır."""
    age = (date.today() - a.birth_date).days
    if not 18 * 365 <= age <= 80 * 365:
        raise ValueError("Yaş 18-80 aralığında olmalıdır")
    row = {
        "pin": a.pin, "first_name": a.first_name.strip(), "last_name": a.last_name.strip(),
        "name_contract_type": a.name_contract_type, "amt_credit": a.amt_credit, "amt_income_total": a.amt_income_total,
        # shortcut: faizsiz təxmini annuitet (kredit / müddət); real hesab üçün faiz dərəcəsi lazımdır
        "amt_annuity": round(a.amt_credit / a.term_months, 2),
        "amt_goods_price": a.amt_goods_price, "name_income_type": a.name_income_type,
        "name_education_type": a.name_education_type, "name_family_status": a.name_family_status,
        "name_housing_type": a.name_housing_type, "cnt_children": a.cnt_children,
        "cnt_fam_members": a.cnt_children + (2 if a.name_family_status in ("Married", "Civil marriage") else 1),
        "flag_own_car": a.flag_own_car, "flag_own_realty": a.flag_own_realty,
        "region_rating_client": a.region_rating_client, "region_rating_client_w_city": a.region_rating_client,
        "flag_work_phone": int(a.has_work_phone), "flag_email": int(a.has_email),
        "flag_mobil": int(a.has_mobile_phone), "flag_cont_mobile": int(a.has_mobile_phone),
        "days_birth": -age,
        "days_employed": -round(a.employed_years * 365) if a.employed_years > 0 else None,
    }
    if DATABASE_URL:
        import psycopg
        try:
            with _pg() as con:  # with: uğurlu bitəndə commit, xətada rollback
                con.execute("SELECT pg_advisory_xact_lock(42)")  # sk_id_curr max+1 yarışını bağlayır
                row["sk_id_curr"] = (con.execute("SELECT max(sk_id_curr) AS m FROM customers").fetchone()["m"] or 0) + 1
                cols = ",".join(f'"{c}"' for c in row)
                con.execute(f"INSERT INTO customers ({cols}) VALUES ({','.join(['%s'] * len(row))})", tuple(row.values()))
        except psycopg.errors.UniqueViolation:
            raise PinTaken
        return {k: row.get(k) for k in _PROFILE}, {k: v for k, v in row.items() if k not in _NON_FEATURE}
    con = sqlite3.connect(DB_PATH)
    try:
        sk = (con.execute("SELECT max(sk_id_curr) FROM customers").fetchone()[0] or 0) + 1
        row["sk_id_curr"] = sk
        cols = ",".join(f'"{c}"' for c in row)
        try:
            con.execute(f"INSERT INTO customers ({cols}) VALUES ({','.join('?' * len(row))})", tuple(row.values()))
        except sqlite3.IntegrityError:
            raise PinTaken
        con.commit()
    finally:
        con.close()
    return {k: row.get(k) for k in _PROFILE}, {k: v for k, v in row.items() if k not in _NON_FEATURE}
