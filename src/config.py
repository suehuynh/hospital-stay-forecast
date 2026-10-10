"""
Project-wide paths, API settings, and column groups.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw" / "sparcs_2024"  # one parquet file per API page
PROCESSED_PATH = DATA_DIR / "processed" / "sparcs_2024_clean.parquet"
FIGURES_DIR = ROOT / "figures"

# SPARCS Hospital Inpatient Discharges (2024): https://health.data.ny.gov/d/sf4k-39ay
BASE_URL = "https://health.data.ny.gov/resource/sf4k-39ay.json"
PAGE_SIZE = 50_000

# All 33 raw columns, in API order. The API leaves out null fields, so a page
# may be missing some columns; every page is reindexed to this list so all
# parquet parts share one schema.
RAW_COLUMNS = [
    "health_service_area",
    "hospital_county",
    "operating_certificate_number",
    "permanent_facility_id",
    "facility_name",
    "age_group",
    "zip_code",
    "gender",
    "race",
    "ethnicity",
    "length_of_stay",
    "type_of_admission",
    "patient_disposition",
    "discharge_year",
    "ccsr_diagnosis_code",
    "ccsr_diagnosis_description",
    "ccsr_procedure_code",
    "ccsr_procedure_description",
    "apr_drg_code",
    "apr_drg_description",
    "apr_mdc_code",
    "apr_mdc_description",
    "apr_severity_of_illness_code",
    "apr_severity_of_illness",
    "apr_risk_of_mortality",
    "apr_medical_surgical",
    "payment_typology_1",
    "payment_typology_2",
    "payment_typology_3",
    "birth_weight",
    "emergency_department_indicator",
    "total_charges",
    "total_costs",
]

# ---------------------------------------------------------------------------
# Column groups
# ---------------------------------------------------------------------------
TARGET = "length_of_stay"

# Known at (or very close to) admission time -> candidate model features.
# ccsr_diagnosis_code is the principal diagnosis, which is finalized at
# discharge. We use it as a stand-in for the admitting diagnosis and note
# this caveat in the report.
ADMISSION_FEATURES = [
    "health_service_area",
    "hospital_county",
    "permanent_facility_id",
    "age_group",
    "zip_code",
    "gender",
    "race",
    "ethnicity",
    "type_of_admission",
    "emergency_department_indicator",
    "payment_typology_1",
    "payment_typology_2",
    "payment_typology_3",
    "birth_weight",
    "ccsr_diagnosis_code",
]

# Determined during or after the stay (or by the discharge grouper).
# Kept in the processed file so EDA can show why they leak, but never
# used as model features.
LEAKAGE = [
    "patient_disposition",
    "ccsr_procedure_code",
    "ccsr_procedure_description",
    "apr_drg_code",
    "apr_drg_description",
    "apr_mdc_code",
    "apr_mdc_description",
    "apr_severity_of_illness_code",
    "apr_severity_of_illness",
    "apr_risk_of_mortality",
    "apr_medical_surgical",
    "total_charges",
    "total_costs",
]

# No information for the model: a constant, or duplicates of another column.
DROP = [
    "discharge_year",  # always 2024
    "operating_certificate_number",  # one-to-one with permanent_facility_id
    "facility_name",  # label for permanent_facility_id
    "ccsr_diagnosis_description",  # label for ccsr_diagnosis_code
]

NUMERIC = ["length_of_stay", "birth_weight", "total_charges", "total_costs"]
