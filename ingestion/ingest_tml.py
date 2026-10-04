"""Download ATP match csvs from TML-database into a UC volume, then rebuild the bronze layer."""
import hashlib
import os

import requests
from pyspark.sql import SparkSession, functions as F

BASE_URL = "https://raw.githubusercontent.com/Tennismylife/TML-Database/master/{year}.csv"
VOLUME = "/Volumes/workspace/tennis_bronze/raw_files"
TABLE = "workspace.tennis_bronze.atp_matches"
YEARS = range(2015, 2026)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def download_year(year: int) -> bool:
    """Save the year's CSV to the volume. Returns True only if the file is new or changed."""
    r = requests.get(BASE_URL.format(year=year), timeout=60)
    r.raise_for_status()
    path = f"{VOLUME}/tml_{year}.csv"

    if os.path.exists(path):
        with open(path, "rb") as f:
            if sha256(f.read()) == sha256(r.content):
                print(f"{year}: unchanged, skipping")
                return False

    with open(path, "wb") as f:
        f.write(r.content)
    print(f"{year}: saved {len(r.content):,} bytes")
    return True


def load_bronze(spark: SparkSession) -> None:
    df = (
        spark.read.csv(f"{VOLUME}/tml_*.csv", header=True)       # all text in bronze
        .withColumn("_source_file", F.col("_metadata.file_name"))
        .withColumn("_ingested_at", F.current_timestamp())
    )
    df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(TABLE)
    print(f"Bronze rebuilt: {spark.table(TABLE).count():,} rows")


if __name__ == "__main__":
    spark = SparkSession.builder.getOrCreate()
    changed = [y for y in YEARS if download_year(y)]
    if changed:
        load_bronze(spark)
    else:
        print("No source changes; bronze left as is")