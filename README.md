# 🧑‍💼 Customer Churn Dashboard

Streamlit dashboard for customer churn prediction using Databricks model serving, Gemini-powered retention insight, PostgreSQL prediction history, and CSV batch scoring.

## Features
- Manual single-customer prediction.
- Prediction from database with editable customer inputs.
- Retention `recommended_action` generated after prediction.
- Prediction history persisted in PostgreSQL.
- Batch prediction from CSV.
- Risk gauge and top risk-driver summary in the UI.

## Tech Stack
- Python 3.10+
- Streamlit
- Requests
- Plotly
- PostgreSQL
- `python-dotenv`


## 🏗️ System Architecture

<img width="5647" height="3107" alt="Architecture" src="https://github.com/user-attachments/assets/7521ea8a-451e-46ff-9db0-71dd6ddf8181" />

## 📂 Project Structure
```text
app.py
styles.css
sample_batch_input.csv

config/
  settings.py                 # environment config and shared constants

data_processing/
  batch_formatter.py          # batch result formatting/export
  csv_parser.py               # CSV parsing and validation

db/
  connection.py               # PostgreSQL connection helper
  repository.py               # customer and prediction persistence
  schema.py                   # schema creation and lightweight migration

features/
  feature_engineering.py      # feature creation and validation

services/
  batch_service.py            # batch prediction orchestration
  customer_db_service.py      # DB/UI mapping helpers
  databricks_api.py           # Databricks API client
  gemini.py                   # retention insight generation
  prediction_service.py       # single prediction orchestration

ui/
  components.py               # shared Streamlit components
  tab_predict.py              # manual, database, and batch tabs

utils/
  constants.py                # CSV and dropdown constants
  helpers.py                  # scoring and UI helper logic
```

## Environment Variables
Create `.env` in the project root:

```env
DATABRICKS_URL=<your_databricks_serving_endpoint>
DATABRICKS_TOKEN=<your_databricks_pat>
DATABRICKS_TIMEOUT=30

GEMINI_API_KEY=<your_gemini_api_key>
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT=15

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=churn_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

DISABLE_OUTBOUND_PROXY=true
```

`DISABLE_OUTBOUND_PROXY=true` is useful for local environments where `HTTP_PROXY` or `HTTPS_PROXY` point to an invalid local proxy. In production, set it based on your network policy.

## Install
```bash
pip install -r requirements.txt
```

## Database Setup
Run schema creation and lightweight migration:

```bash
python -m db.schema
```

This creates:
- `customers`
- `predictions`

It also ensures `recommended_action` exists on `predictions`.

## Run Locally
```bash
streamlit run app.py
```

## Batch Prediction CSV
Required columns:

```text
Age, Gender, Tenure, Usage Frequency, Support Calls, Payment Delay,
Subscription Type, Contract Length, Total Spend, Last Interaction
```

Accepted values:
- `Gender`: `Male` or `Female`
- `Subscription Type`: `Basic`, `Standard`, `Premium`
- `Contract Length`: `Monthly` / `Quarterly` / `Annual` or `1 month` / `3 months` / `12 months`

Quick test file:
- `sample_batch_input.csv`

## Notes
- Manual prediction results are stored in Streamlit `session_state`.
- Database predictions store history in PostgreSQL.
- Retention insight uses Gemini and falls back to rule-based actions if Gemini is unavailable.