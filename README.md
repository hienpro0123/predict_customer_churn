# Customer Churn Dashboard

A Streamlit dashboard for predicting customer churn using a Databricks Model Serving endpoint.

## What this project does
- Collects customer profile and subscription inputs.
- Builds engineered features for model inference.
- Calls Databricks endpoint for churn prediction.
- Displays prediction result with risk gauge and top risk drivers.
- Supports **Batch Predict (CSV)** for multiple customers in one run.

## Tech stack
- Python 3.10+
- Streamlit
- Requests
- Plotly
- python-dotenv (optional fallback to local parser already included)

## Project structure
```text
app.py                       # Main Streamlit app
styles.css                   # UI styling
sample_batch_input.csv       # Sample CSV for batch prediction

config/
  settings.py                # Env config + feature column definitions

features/
  feature_engineering.py     # Feature creation and input validation

services/
  databricks_api.py          # Databricks API client (single + batch)

ui/
  components.py              # UI sections and rendering

utils/
  helpers.py                 # Parsing/normalization helpers
```

## Environment variables
Create `.env` in project root:

```env
DATABRICKS_URL=<your_databricks_serving_endpoint>
DATABRICKS_TOKEN=<your_pat_token>
DATABRICKS_TIMEOUT=30
```

## Install dependencies
```bash
pip install streamlit requests plotly python-dotenv
```

## Run locally
```bash
streamlit run app.py
```

## Batch Predict (CSV)
### Required columns
```text
Age, Gender, Tenure, Usage Frequency, Support Calls, Payment Delay,
Subscription Type, Contract Length, Total Spend, Last Interaction
```

### Accepted values
- `Gender`: `Male` or `Female`
- `Subscription Type`: `Basic`, `Standard`, `Premium`
- `Contract Length`: `Monthly` / `Quarterly` / `Annual` or `1 month` / `3 months` / `12 months`

### Quick test
Use the included file:
- `sample_batch_input.csv`

## Notes
- Prediction result persistence uses Streamlit `session_state`.
- Python cache files (`__pycache__`, `*.pyc`) are ignored by `.gitignore`.
