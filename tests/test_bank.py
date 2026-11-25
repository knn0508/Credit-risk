"""api/bank.py SQLite yolu (DATABASE_URL yoxdur): PIN tapılır, yeni müraciətçi yazılır, təkrar PIN → PinTaken."""
import sqlite3
from datetime import date

import pytest

from api import bank


@pytest.fixture
def db(tmp_path, monkeypatch):
    p = tmp_path / "t.db"
    con = sqlite3.connect(p)
    cols = ["pin TEXT PRIMARY KEY", "first_name TEXT", "last_name TEXT", "sk_id_curr INTEGER UNIQUE NOT NULL"] + [
        f'"{c}"' for c in ("name_contract_type", "amt_credit", "amt_income_total", "amt_annuity", "amt_goods_price",
                           "name_income_type", "name_education_type", "name_family_status", "name_housing_type",
                           "cnt_children", "cnt_fam_members", "flag_own_car", "flag_own_realty", "region_rating_client",
                           "region_rating_client_w_city", "flag_work_phone", "flag_email", "flag_mobil",
                           "flag_cont_mobile", "days_birth", "days_employed")]
    con.execute(f"CREATE TABLE customers ({', '.join(cols)})")
    con.commit()
    con.close()
    monkeypatch.setattr(bank, "DATABASE_URL", None)
    monkeypatch.setattr(bank, "DB_PATH", p)
    return p


def _app(pin="AB12345"):
    return bank.Application(
        pin=pin, first_name="A", last_name="B", birth_date=date(1990, 1, 1), name_contract_type="Cash loans",
        amt_credit=1000, term_months=10, amt_income_total=500, name_income_type="Working", employed_years=2,
        name_education_type="Higher education", name_family_status="Single / not married",
        name_housing_type="With parents", cnt_children=0, flag_own_car="N", flag_own_realty="N",
        region_rating_client=2, has_work_phone=False, has_mobile_phone=True, has_email=True)


def test_create_find_duplicate(db):
    assert bank.find_customer("AB12345") is None
    profile, applicant = bank.create_customer(_app())
    assert profile["first_name"] == "A" and "pin" not in applicant and applicant["sk_id_curr"] == 1
    found = bank.find_customer("AB12345")
    assert found is not None and found[1]["amt_credit"] == 1000
    with pytest.raises(bank.PinTaken):
        bank.create_customer(_app())


def test_valid_pin():
    assert bank.valid_pin("AB12345") and not bank.valid_pin("ABCDEFG") and not bank.valid_pin("AB1234")
