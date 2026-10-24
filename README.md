# hospital-stay-forecast

Regression model to forecast real-time length of stay of any patients at admission time at the hospitals.

## Overview

Hospitals plan beds, staff and discharges around how long each patient will stay. The goal of this project is to predict the length of stay (`los`, in days) of a patient once admitted, using only information known at admission. We use patient information, medical information collected at admission, and hospital information to predict the length of stay. Our regression model would have potential impacts on early bed-turnover scheduling and calibrating staffing ratios using the predicted length of stay.

The data is the **SPARCS Hospital Inpatient Discharges (De-identified), 2024** dataset from the New York State Department of Health: 2,196,737 inpatient discharges and 33 columns, one row per discharge.

- Source: <https://health.data.ny.gov/d/sf4k-39ay>
- Column-by-column description: [`data/data_documentation.txt`](data/data_documentation.txt)

The analysis is in one notebook, `src/sparcs_los_eda.ipynb`, which is organised in four sections:

1. **Setup and load:** downloads the data from the Socrata (SODA) API in pages of 50,000 rows and caches it as parquet.
2. **Data understanding:** column types, missing values, and the target variable.
3. **Data cleaning:** every decision is explained next to the code that applies it. Includes filtering columns for data leakage and removing rows.
4. **EDA charts:** the distribution of length of stay, and how it varies with diagnosis, procedure, age, payer, race and emergency department use.

## Main findings from the EDA

- Stays are short and strongly right-skewed. About half of all discharges end within 3 days, but the mean is about 6 days and the 95th percentile is 19 days. 1.9% of stays are longer than 30 days.
- The source caps the target at 120 days (`120+`), so the target is right-censored there.
- The principal diagnosis separates the typical stay strongly. Among the 15 most common diagnoses the median runs from about 2 to about 13 days.
- Among the 12 most common procedure categories the median runs from about 2 to about 7 days.
- Of the patient characteristics compared (age group, primary payer, race, emergency department visit), age group separates the median stay the most (2 to 4 days). No single characteristic separates long stays from short ones by itself.

## Repository structure

```
hospital-stay-forecast/
├── README.md
├── LICENSE
├── environment.yml          # conda environment (pinned versions)
├── data/
│   ├── data_documentation.txt   # description of the source columns
│   ├── raw/                    # downloaded data, created by the notebook, not committed
│   └── processed/              # cleaned data, created by the notebook, not committed
├── src/
│   └── sparcs_los_eda.ipynb    # data understanding, cleaning and EDA
├── figures/                 # charts saved by the notebook
├── results/
└── report/
```

## Technical setup

### Python and package versions

The code was developed with **Python 3.14**. Package versions are listed in [`environment.yml`](environment.yml).

### 1. Create the environment

**Prerequisites:** [git](https://git-scm.com/) and [conda](https://docs.conda.io/en/latest/) (Miniconda, Anaconda or Miniforge).

1. Clone the repository.

   ```bash
   git clone https://github.com/suehuynh/hospital-stay-forecast.git
   ```

2. Move into the project folder.

   ```bash
   cd hospital-stay-forecast
   ```

3. Create the conda environment from `environment.yml`. This installs Python and all the packages, and only needs to be done once.

   ```bash
   conda env create -f environment.yml
   ```

4. Activate the environment. Do this every time you open a new terminal to work on the project.

   ```bash
   conda activate hospital-stay-forecast
   ```

### 2. (Optional) Add a Socrata app token

Downloading about 2.2 million rows is faster and less likely to be throttled with an app token. The notebook works without one.

Create a file named `.env` in the project root:

```
APP_TOKEN=your_token_here
```

You can request a free token at <https://dev.socrata.com/register>. `.env` is listed in `.gitignore`, so it is never committed.

### 3. Run the notebook

```bash
jupyter lab
```

Open `src/sparcs_los_eda.ipynb` and run all cells (Kernel, then Restart and Run All).

- Run it from the `src/` folder (open the notebook from Jupyter's file browser). The paths in the notebook (`../data`, `../figures`) are relative to `src/`.
- The first run downloads the data and saves it to `data/raw/sparcs_2024_raw.parquet`. Later runs load from that cache. Delete the file to force a fresh download.
- The notebook writes the cleaned table to `data/processed/sparcs_2024_final.parquet` and saves the charts to `figures/`.

## Figures

| File | What it shows |
|---|---|
| `los_distribution_1_to_30_days.png` | Length of stay for stays of 1 to 30 days |
| `los_distribution_all_stays.png` | Every stay from 1 to 120 days, on a log scale |
| `category_shares.png` | Share of discharges by level of each categorical feature |
| `cramers_v_heatmap.png` | Association between categorical features |
| `diagnosis_vs_los.png` | Length of stay for the 15 most common diagnoses |
| `procedure_vs_los.png` | Length of stay for the 12 most common procedure categories |
| `los_by_group.png` | Length of stay by age group, primary payer, race and emergency department use |

## References

1. 3M Health Information Systems. *3M All Patient Refined Diagnosis Related Groups (APR DRG) Methodology Overview*, 2023. <https://hcup-us.ahrq.gov/db/nation/nis/3M_aprdrg_methodology_overview.pdf>
2. Xinyu Chen, Yifan Wang, Elinor Schoenfeld, Mary Saltz, Joel Saltz, and Fusheng Wang. *Spatio-temporal analysis for New York State SPARCS data*. AMIA Joint Summits on Translational Science Proceedings, 2017:483–492, 2017.
3. Jonathan E. Helm, Shervin AhmadBeygi, and Mark P. Van Oyen. *Design and analysis of hospital admission control for operational effectiveness*. Production and Operations Management, 20(3):359–374, 2011. <https://doi.org/10.1111/j.1937-5956.2011.01231.x>
4. Victor Koltenyuk, Jay Ayar, Elizabeth Drugge, and Anna R. Cooper. *Determinants of discharge disposition for adult patients admitted with pathologic fractures in New York State: A SPARCS study, 2020–2022*. Montefiore Einstein Journal of Musculoskeletal Medicine and Surgery, 5:30498929261440188, 2026. <https://doi.org/10.1177/30498929261440188>
5. New York State Department of Health. *Hospital Inpatient Discharges (SPARCS De-Identified): 2024*, 2024. <https://health.data.ny.gov/d/sf4k-39ay>
6. Jonathan S. Olshaker and Niels K. Rathlev. *Emergency department overcrowding and ambulance diversion: The impact and potential solutions of extended boarding of admitted patients in the emergency department*. The Journal of Emergency Medicine, 30(3):351–356, 2006. ISSN 0736-4679. <https://doi.org/10.1016/j.jemermed.2005.05.023>
7. Socrata. *Socrata Open Data API (SODA) Documentation: Hospital Inpatient Discharges (SPARCS De-Identified) Dataset sf4k-39ay*. <https://dev.socrata.com/foundry/health.data.ny.gov/sf4k-39ay>
8. Beibei Yuan and Qiang Su. *Data-driven automated admission control for hospital bed allocation: A dynamic threshold policy*. In 2026 IEEE International Conference on Mechatronics and Automation (ICMA), pages 1062–1066, 2026. <https://doi.org/10.1109/ICMA69663.2026.11647484>

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

The data is published by the New York State Department of Health and is not redistributed in this repository. See the [dataset page](https://health.data.ny.gov/d/sf4k-39ay) for its terms of use.
