# M-Lab India network-condition analysis

Four notebooks:

- **`outlier.ipynb`** — loads the combined raw CSVs from `mlab_data/`, inspects
  coverage, missingness and geography, applies reviewed exact-ASN non-access exclusions and removes
  invalid/sentinel rows, exports
  the cleaned dataset plus the removed rows, and breaks the clean data down by connection type
  (mobile vs. broadband, from `client_as_name`).
- **`main.ipynb`** — reads only the cleaned CSVs and shows coverage, distribution/ECDF and
  geo-spatial plots on the clean data. Figures label sample sizes, units, and key summary statistics;
  distributions show counts per bin and loss is displayed as a percentage. No outlier-detection code lives here.
- **`clustering.ipynb`** — k-means network-quality profiles on the clean data (download:
  throughput/RTT/loss; upload: throughput/RTT), with k selected across 2–6 via elbow + silhouette,
  a ranked presentation table, nearest-real-row lookup per centroid, and an ASN/state concentration
  check on the worst-ranked profile.
- **`gmm.ipynb`** — the same question via a Gaussian Mixture Model instead of k-means: BIC/AIC/
  silhouette across k = 2–6, a ranked profile table (mean *and* median per feature), and a
  membership-probability overlap report (how many rows sit ambiguously between two profiles, which
  k-means' hard labels can't show).

Labels in both clustering notebooks (Excellent/Good/Fair/...) describe the dominant relative
limitation (higher-performing, throughput-constrained, or loss-affected); they are not absolute
service-quality grades, and the two notebooks are independent methods run on the same clean data —
neither is the "official" answer.

## Setup

From the repository root, create the environment:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r mlab_analysis/requirements.txt
```

Open any notebook in the IDE and select `.venv/bin/python` as its kernel/interpreter. Run
`outlier.ipynb` first to create the clean CSVs; `main.ipynb` is the follow-up exploration. The
`clustering.ipynb` and `gmm.ipynb` notebooks are optional analyses and are not part of the current
combined-data run.

Default inputs: `mlab_data/combined/2026-06-18_to_2026-11-04/download.csv` and
`mlab_data/combined/2026-06-18_to_2026-11-04/upload.csv`. Outputs for this dataset are written to
`outputs/analysis/2026-06-18_to_2026-11-04/` (tables/JSON at the top level and figures under
`figures/01_data_quality/`, `02_cleaning_evidence/`, `03_clean_data/`, and
`04_connection_type/`). The notebooks display supplementary raw-data charts inline without saving
them, avoiding duplicate and nonessential plot files. Set `MLAB_RAW_DATA_DIR` and `MLAB_OUTPUT_DIR` to run a
different dated input into its own output folder. The earlier-period analysis is kept at
`outputs/analysis/2026-06-18_to_2026-09-15/`.

To create separate percentile tables for the cleaned download and upload data, run:

```bash
.venv/bin/python mlab_analysis/percentile_summary.py
```

The script writes CSVs to `outputs/analysis/2026-06-18_to_2026-11-04/percentiles/` and prints both
tables. Throughput reports P1, P5, P10, P15, P20, P25 and P50; RTT and packet loss report P50, P75,
P80, P85, P90, P95 and P99, along with mean, median and sample standard deviation. Upload packet
loss is unavailable in the cleaned data and is clearly marked as such. Use `--input-dir` and
`--output-dir` to select another dated analysis run.

## What gets removed, and what doesn't

- **Domain-invalid (removed):** a clustering feature missing/non-finite, throughput or RTT
  non-positive, download loss outside `[0, 1]`, a duplicated measurement ID, or an exact match to
  the 32-bit unsigned-integer overflow sentinel (`(2**32 - 1) / 1000` ms) in `min_rtt_ms`.
- **Non-access ASN policy (removed):** exact `client_asn` match to a reviewed
  list (`non_access_asn_rules.csv`) of cloud, hosting, CDN, data-centre, proxy/security, enterprise,
  government/institutional or academic-network operators — never a name-substring guess, since
  Indian access ISPs legitimately use words like "cloud" or "networks" in their names. Built in two
  earlier review rounds, then a combined-period review that added named educational institutions,
  enterprise organizations, PI Data Centers, Software Technology Parks of India, Centre for Railway
  Information Systems, and the explicitly Wi-Fi-named IRG WIFI Service ASN. Every exclusion uses an
  exact ASN match. `additional_non_access_asn_review.csv` records the new rules and removed row counts by
  direction. Ordinary access ISPs with enterprise-sounding names — e.g. BSNL's "National Internet
  Backbone", RailTel, Gatik Business Solutions, and regional broadband operators — are retained.
- **Wi-Fi limitation:** M-Lab CSVs do not identify SSIDs or whether a test used a home router,
  subscriber Wi-Fi, or a public/commercial hotspot. The two IRG WIFI Service rows were excluded based
  on the explicit operator name, but the data does not prove they were hotspot traffic and does not
  support a reliable blanket commercial-Wi-Fi filter.
- **Statistical tail (kept):** extreme-but-plausible points (very low throughput + very high RTT/loss)
  that pass every validity check and aren't matched by the exact-ASN exclusion policy. Evidence in `outlier.ipynb` Section
  8a shows they're spread across many ASNs/states/dates with an internally consistent poor-path
  signature, not a data artifact — so they stay in the clean export.

## Cleaning and exploration outputs (inside the selected `outputs/analysis/<date-range>/` folder)

- `download_clean.csv` / `upload_clean.csv` — the cleaned datasets.
- `download_removed_outliers.csv` / `upload_removed_outliers.csv` — everything removed, tagged with
  a `removal_reason` column.
- `download_connection_type.csv` / `upload_connection_type.csv` — row counts, percentages and median
  throughput by connection type (Mobile / Broadband / Mixed — Jio and BSNL can't be split further by
  ASN name alone, since both route mobile and fixed customers under the same corporate ASN).
- `download_stats_comparison.csv` / `upload_stats_comparison.csv` — mean/median/std/P99, original vs.
  clean. `download_descriptive_stats_{original,clean}.csv` / `upload_descriptive_stats_{original,clean}.csv`
  add mode, min and max.
- `outlier_removal_summary.csv`, `cleaning_summary.json` — row counts and percentages by category.
- `non_access_asn_rules.csv` — the exact-ASN rule table used for non-access exclusions, with
  round-by-round comments in `outlier.ipynb` Section 6 documenting what
  was checked and explicitly kept (e.g. "Skynet"-branded ISPs, "171 Incorporation") vs. removed.
- Optional outputs from `clustering.ipynb` and `gmm.ipynb` are generated only when those notebooks
  are explicitly run; they are not included in the current combined-data analysis.

## Status / next stage

The prior blocker — sparse date coverage in an earlier sample — is resolved: the current raw input
files cover all 140 expected days for both directions. Run `outlier.ipynb` first to create the clean
files for the selected date range, then run `main.ipynb` for exploration. The current combined
dataset has cleaning and exploration outputs only; the optional clustering notebooks were not run
for it. Existing k-means/GMM results and the open modeling questions below refer to the preserved
earlier-period analysis, not the combined dataset. These models are experimental and do not replace
or modify the percentile-based Mahimahi conditions.

**Earlier-period GMM question:** for both directions, BIC/AIC kept improving through k = 6, the top
of the tested range (download: BIC still dropped by ~2,159 from k=5 to k=6), so the statistical
optimum may lie above 6. The earlier GMM download ranking also put "Excellent" only marginally above
"Good" (quality score 2.25 vs 2.24); review those archived results before presenting them.
