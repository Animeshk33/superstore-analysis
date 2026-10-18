# Superstore Business Analysis

A learning project: analyze the Superstore sales dataset the way a business
analyst would — ask real questions, answer them with data, and present
findings as charts and a dashboard.

## Project layout

```
data/raw/        the original CSV (not committed — see .gitignore)
scripts/         Python analysis scripts
outputs/charts/  generated chart images
outputs/         final dashboard.html
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Workflow

1. Explore and clean the data (`scripts/01_explore.py`)
2. Answer business questions with aggregations (`scripts/02_analysis.py`)
3. Generate charts (`scripts/03_charts.py`)
4. Assemble `outputs/dashboard.html`
