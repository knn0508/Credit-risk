"""Konteyner start-ında model bundle-ı R2-dən (S3 API) BUNDLE_DIR-ə yükləyir. Env: R2_ACCOUNT_ID, R2_ACCESS_KEY_ID,
R2_SECRET_ACCESS_KEY, R2_BUCKET, MODEL_VERSION. Fayl siyahısı: docs/contracts/model-bundle.md (runtime üçün lazım olanlar)."""
import os
from pathlib import Path

import boto3

FILES = ["model.joblib", "calibrator.joblib", "feature_names.json", "metadata.json", "risk_policy.json", "background.parquet"]


def main() -> None:
    dest = Path(os.environ.get("BUNDLE_DIR", "/models/current"))
    dest.mkdir(parents=True, exist_ok=True)
    s3 = boto3.client(
        "s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"], aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
        region_name="auto")
    prefix = f"models/{os.environ['MODEL_VERSION']}/"
    for f in FILES:
        s3.download_file(os.environ["R2_BUCKET"], prefix + f, str(dest / f))
        print("fetched", f, flush=True)


if __name__ == "__main__":
    main()
