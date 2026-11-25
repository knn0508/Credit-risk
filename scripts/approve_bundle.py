"""Bundle-a risk siyasətini yazır və statusunu yeniləyir (Agent 01-in "təsdiq" addımı; docs/contracts/model-bundle.md).

İstifadə (repo kökündən):
  python scripts/approve_bundle.py artifacts/models/<version> --approved-by "Ad Soyad"

Əvvəl `python -m src.evaluation.run_oof artifacts/models/<version>` işlənməlidir: o, calibrator.joblib və
reports/oof_<version>.json yaradır. Hədlər həmin hesabatdan TAM DƏQİQLİKLƏ götürülür (yuvarlaqlaşdırma yoxdur).
Biznes təsdiqi bu skriptlə verilmir: business_approval həmişə "pending" yazılır (decisions/0004: yalnız demo/prototip).
--approved-by verilməsə status "validated" olur (API bundle-ı yalnız ALLOW_DEV=1 ilə yükləyir).
"""
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bundle", help="artifacts/models/<version>")
    ap.add_argument("--oof-report", help="default: reports/oof_<version>.json")
    ap.add_argument("--approved-by", help="verilərsə validation_status=approved, verilməzsə validated")
    ap.add_argument("--policy-version", default=None)
    a = ap.parse_args()

    b = Path(a.bundle)
    meta_p = b / "metadata.json"
    if not meta_p.exists():
        sys.exit(f"{meta_p} yoxdur: bundle yolunu yoxlayın")
    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    version = meta["model_version"]
    if not (b / "calibrator.joblib").exists():
        sys.exit("calibrator.joblib yoxdur: əvvəl python -m src.evaluation.run_oof <bundle> işlədin")
    rep_p = Path(a.oof_report or f"reports/oof_{version}.json")
    if not rep_p.exists():
        sys.exit(f"{rep_p} yoxdur: əvvəl run_oof işlədin (və ya --oof-report verin)")
    rep = json.loads(rep_p.read_text(encoding="utf-8"))
    prop = rep["proposal"]
    low, med = prop["low_max"], prop["medium_max"]
    if not (0 < low < med < 1):
        sys.exit(f"yanlış hədlər: low_max={low}, medium_max={med}")

    pol_version = a.policy_version or f"1.0-{version}-provisional"
    policy = {"version": pol_version, "status": "approved_provisional", "low_max": low, "medium_max": med,
              "business_approval": "pending"}
    (b / "risk_policy.json").write_text(json.dumps(policy, indent=2), encoding="utf-8")

    meta["calibrated"] = True
    meta["calibration_method"] = rep.get("calibration", {}).get("chosen", meta.get("calibration_method"))
    meta["risk_policy_version"] = pol_version
    if a.approved_by:
        meta["validation_status"] = "approved"
        meta["approved_by"] = f"{a.approved_by} (texniki; biznes təsdiqi pending)"
    else:
        meta["validation_status"] = "validated"
    meta_p.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{version}: status={meta['validation_status']} calibrated=True low_max={low} medium_max={med}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
