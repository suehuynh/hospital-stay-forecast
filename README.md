# hospital-stay-forecast
Regression model to forecast real-time length of stay of any patients at admission time at the hospitals.

Data: [SPARCS Hospital Inpatient Discharges (2024)](https://health.data.ny.gov/d/sf4k-39ay), about 2.2M rows.

## Environment setup

```bash
conda env create -f environment.yml     # first time only (use `conda env update -f environment.yml --prune` after changes)
conda activate hospital-stay-forecast
python -m ipykernel install --user --name hospital-stay-forecast --display-name "Python (hospital-stay-forecast)"
```

The environment installs this repo as an editable package (`pip install -e .`), so `from src... import ...` works from the notebooks and from any directory. In Jupyter, pick the **Python (hospital-stay-forecast)** kernel.

Optional: add `APP_TOKEN=<your Socrata app token>` to a `.env` file at the repo root to avoid API throttling.

## Getting the data

The data is not committed to git. Rebuild it locally:

```bash
python -m src.download   # ~2.2M rows from the API -> data/raw/sparcs_2024/part-*.parquet (resumable)
python -m src.clean      # typed, cleaned table   -> data/processed/sparcs_2024_clean.parquet
```

Read only the columns you need: `pd.read_parquet(PROCESSED_PATH, columns=[...])`. The cleaned table uses categorical dtypes, so it takes about 115 MB in memory, compared with about 1.4 GB for the raw strings.

## Layout

```
src/config.py     paths, API settings, column groups (admission features / leakage / target)
src/download.py   API download (python -m src.download)
src/clean.py      cleaning (python -m src.clean)
notebooks/        01_load_data (collection walkthrough), 02_eda (EDA; figures -> figures/)
data/raw/         API dump, never edited (gitignored)
data/processed/   cleaned parquet (gitignored)
figures/          figures for the report
```

## Feature policy

The model predicts LOS **at admission**, so only `ADMISSION_FEATURES` in `src/config.py` may be used as inputs. Columns in `LEAKAGE` are set during or after the stay: charges and costs, disposition, procedures, and the APR DRG/MDC/severity/mortality fields from the discharge grouper. They are kept in the processed data only for EDA. `ccsr_diagnosis_code` is the principal diagnosis, finalized at discharge, and is used as a stand-in for the admitting diagnosis.
