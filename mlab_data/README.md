# M-Lab India datasets

All folder date ranges are inclusive. This snapshot was assembled on 2026-11-05 and contains
measurements through 2026-11-04. The CSVs are grouped by collection period; `combined/` is the
dataset to use for analysis and cleaning.

## Folder layout

```text
mlab_data/
├── periods/
│   ├── 2026-06-18_to_2026-09-15/
│   │   ├── download.csv
│   │   └── upload.csv
│   └── 2026-09-16_to_2026-11-04/
│       ├── download.csv
│       └── upload.csv
├── combined/
│   └── 2026-06-18_to_2026-11-04/
│       ├── download.csv
│       └── upload.csv
└── archive/
    └── legacy_partial_2026-07-28_to_2026-09-15/
        ├── download.csv
        └── upload.csv
```

The archived legacy files are an older, incomplete extract and were **not** used to create the
combined data. The old download filename was misspelled `downlaod.csv`; it is named `download.csv`
here. That archive has only 2 distinct dates in its download file and 6 in its upload file.

## Coverage and row counts

| Dataset | Inclusive dates | Calendar dates present | Download rows | Upload rows | Total rows |
|---|---|---:|---:|---:|---:|
| Earlier period | 2026-06-18 to 2026-09-15 | 90 / 90 | 28,133 | 33,001 | 61,134 |
| Added period | 2026-09-16 to 2026-11-04 | 50 / 50 | 28,232 | 31,550 | 59,782 |
| Combined | 2026-06-18 to 2026-11-04 | 140 / 140 | 56,365 | 64,551 | 120,916 |

The combined files are the earlier-period rows followed by the added-period rows. No date filtering
or data cleaning was applied, and measurement IDs are unique within each combined file.

The download schemas match across periods. The earlier upload file has 19 columns and the added
upload file has 22; the combined upload file keeps the union of columns, leaving fields blank where
they were not present in the earlier source.

## Analysis input

`mlab_analysis/outlier.ipynb` reads the combined files from
`combined/2026-06-18_to_2026-11-04/`. Run that notebook to begin the cleaning workflow.
Analysis outputs are stored separately by date range under
`../outputs/analysis/2026-06-18_to_2026-09-15/` (earlier-period results) and
`../outputs/analysis/2026-06-18_to_2026-11-04/` (combined-data results).
