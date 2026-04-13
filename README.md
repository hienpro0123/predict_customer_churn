# Customer Churn Fullstack App

FastAPI backend and React frontend for customer churn prediction, batch scoring, retention insight generation, and PostgreSQL-backed prediction history.

## Architecture

Data flow:

`Frontend -> FastAPI routers -> services -> database / external model APIs -> response`

## Project Structure

```text
backend/
  core/
  database/
  models/
  routers/
  schemas/
  services/
  utils/
  main.py

frontend/
  src/
    api/
    components/
    pages/

tests/
docker/
docker-compose.yml
requirements.txt
```

## Preserved Functionality

- Single-customer prediction
- Prediction from stored PostgreSQL customer records
- Prediction history persistence
- Batch CSV validation and scoring
- Databricks model serving integration
- Gemini retention recommendation with fallback strategy
- Risk level and top churn-driver analytics

## Backend

- `routers/`: REST endpoints for health, prediction, and customer workflows
- `services/`: feature engineering, scoring, CSV parsing, analytics, customer logic
- `models/`: SQLAlchemy ORM entities for `customers` and `predictions`
- `schemas/`: Pydantic request/response models
- `core/`: environment-driven settings
- `database/`: engine, sessions, and bootstrap
- `utils/`: shared constants and helpers

Run locally:

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## Frontend

The frontend reproduces the original three user flows:

- Single Prediction
- Predict From Database
- Batch Prediction

Run locally:

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` if the backend is not available at `http://localhost:8000/api`.

## Environment

Use the existing `.env` values for Databricks, Gemini, and PostgreSQL. Recommended variables:

```env
DATABRICKS_URL=
DATABRICKS_TOKEN=
DATABRICKS_TIMEOUT=30

GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT=15

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=churn_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

FRONTEND_ORIGIN=http://localhost:5173
DISABLE_OUTBOUND_PROXY=true
```

## Docker

`docker-compose.yml` now runs PostgreSQL, pgAdmin, the FastAPI backend, and the React frontend.

## Tests

```bash
pytest
```
