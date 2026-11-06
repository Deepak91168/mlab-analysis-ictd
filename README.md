# M-Lab network analysis

Source repository for the M-Lab analysis notebooks and percentile script. Raw datasets and
generated analysis outputs are intentionally excluded from Git; transfer `mlab_data/` separately.

## Setup

From the project directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r mlab_analysis/requirements.txt
```

Copy the data into the documented layout in [`mlab_data/README.md`](mlab_data/README.md).
Then run `mlab_analysis/outlier.ipynb` followed by `mlab_analysis/main.ipynb`.
The percentile tables can be generated with:

```bash
.venv/bin/python -m mlab_analysis.percentile_summary
```

See [`mlab_analysis/README.md`](mlab_analysis/README.md) for analysis details and output locations.
