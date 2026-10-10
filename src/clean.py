"""Clean the raw SPARCS 2024 data into a typed, compact parquet file.

Usage:
    python -m src.clean

Reads the raw parts written by ``src.download`` and writes
``data/processed/sparcs_2024_clean.parquet``.

Cleaning choices (see the report for the reasoning):
- length_of_stay: the API caps it at "120+", which becomes 120, with a
  ``los_capped`` flag so we can tell the capped stays apart.
- Charges, costs, and birth weight become floats. Birth weight is only
  recorded for newborns, so it is NaN for everyone else ("UNKN" also -> NaN).
- About 5k rows have facility and location redacted for confidentiality.
  They are kept, and ``facility_redacted`` flags them.
- Missing payment_typology_2/3 means there is no secondary/tertiary payer,
  so it is filled with "None" rather than treated as missing.
- "Not Available" (type_of_admission) and "Undetermined"/"Not Applicable"
  (APR fields) become real missing values. "Unknown" ethnicity, gender "U",
  and zip "OOS" (out of state) are kept as their own levels because they are
  common and carry meaning.
- Text columns become pandas categoricals (ordered where there is a natural
  order), which cuts memory by roughly 10x compared with plain strings.
- Exact duplicate rows are reported but kept: there is no patient id, so two
  identical rows can be two different patients.
"""

import pandas as pd

from src.config import PROCESSED_PATH
from src.download import load_raw

LOS_CAP = 120

ORDERED_LEVELS = {
    "age_group": ["0-17", "18-29", "30-49", "50-69", "70 or Older"],
    "apr_severity_of_illness": ["Minor", "Moderate", "Major", "Extreme"],
    "apr_risk_of_mortality": ["Minor", "Moderate", "Major", "Extreme"],
}

# Values that really mean "missing" for a given column.
MISSING_SENTINELS = {
    "type_of_admission": ["Not Available"],
    "apr_severity_of_illness": ["Undetermined"],
    "apr_risk_of_mortality": ["Undetermined"],
    "apr_medical_surgical": ["Not Applicable"],
    "facility_name": ["Redacted for Confidentiality"],
}


def clean(raw):
    df = raw.copy()

    # Constant or duplicate columns carry no information.
    assert df["discharge_year"].nunique() == 1, "expected a single discharge year"
    df = df.drop(columns=["discharge_year", "operating_certificate_number"])

    # Target
    los = df["length_of_stay"].str.strip()
    df["los_capped"] = los.eq(f"{LOS_CAP}+").astype(bool)
    df["length_of_stay"] = pd.to_numeric(los.str.rstrip("+")).astype("int16")

    # Numeric columns
    for col in ["birth_weight", "total_charges", "total_costs"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float32")
    df["apr_severity_of_illness_code"] = pd.to_numeric(
        df["apr_severity_of_illness_code"], errors="coerce"
    ).astype("Int8")
    # Severity code 0 means "Undetermined".
    df["apr_severity_of_illness_code"] = df["apr_severity_of_illness_code"].replace(0, pd.NA)

    # Missing values
    df["facility_redacted"] = df["permanent_facility_id"].isna()
    for col, sentinels in MISSING_SENTINELS.items():
        df[col] = df[col].replace(sentinels, pd.NA)
    for col in ["payment_typology_2", "payment_typology_3"]:
        df[col] = df[col].fillna("None")

    # Categoricals
    for col in df.columns:
        if col in ORDERED_LEVELS:
            df[col] = pd.Categorical(df[col], categories=ORDERED_LEVELS[col], ordered=True)
        elif pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].astype("category")

    return df


def summarize(raw, df):
    print(f"Rows: {len(raw):,} raw -> {len(df):,} clean")
    print(f"Columns: {raw.shape[1]} raw -> {df.shape[1]} clean")
    print(f"Exact duplicate rows (kept): {raw.duplicated().sum():,}")
    print(f"Capped stays (120+): {df['los_capped'].sum():,}")
    print(f"Redacted facility rows: {df['facility_redacted'].sum():,}")
    mem_raw = raw.memory_usage(deep=True).sum() / 1e6
    mem_clean = df.memory_usage(deep=True).sum() / 1e6
    print(f"Memory: {mem_raw:,.0f} MB raw -> {mem_clean:,.0f} MB clean")

    missing = df.isna().mean().mul(100).round(2)
    missing = missing[missing > 0].sort_values(ascending=False)
    print("\nMissing values (% of rows):")
    print(missing.to_string())


def main():
    raw = load_raw()
    df = clean(raw)

    assert df["length_of_stay"].notna().all()
    assert df["length_of_stay"].between(1, LOS_CAP).all()

    summarize(raw, df)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(PROCESSED_PATH, index=False)
    print(f"\nSaved {PROCESSED_PATH}")


if __name__ == "__main__":
    main()
