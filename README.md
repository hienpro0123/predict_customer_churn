# Customer Churn Fullstack App

A full-stack customer churn prediction application built with FastAPI, React (Vite), and PostgreSQL. The system supports single-customer prediction, prediction from stored database records, batch CSV scoring, prediction history tracking, and AI-assisted retention recommendations.

## System Architecture

<img width="5647" height="3107" alt="Architecture" src="img/flow.jpg" />

## Main Features

- Single-customer churn prediction from a manual form
- Churn prediction for customers stored in PostgreSQL
- Prediction history persistence per customer
- Batch prediction from CSV upload
- Churn probability, predicted label, risk level, and churn-driver analytics
- Databricks Model Serving integration for scoring
- Gemini integration for retention recommendations

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
  dockerfile

frontend/
  src/
    api/
    components/
    pages/
  dockerfile
  vite.config.js

img/
docker-compose.yml
.env
sample_batch_input.csv
README.md
```

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- PostgreSQL
- Uvicorn

### Frontend

- React 18
- Vite
- Fetch API

### External Services

- Databricks Model Serving
- Gemini API

## Backend Overview

The backend follows a service-oriented FastAPI structure:

- `routers/`: REST API routes
- `services/`: feature engineering, prediction, analytics, CSV parsing, Databricks, Gemini, and customer workflows
- `models/`: SQLAlchemy ORM models for `customers` and `predictions`
- `schemas/`: request and response models
- `database/`: engine, session management, and schema initialization
- `core/`: application settings loaded from `.env`
- `utils/`: shared constants and helper utilities

### Database Tables

#### `customers`

Stores customer input data used for database-backed prediction:

- `id`
- `age`
- `gender`
- `tenure`
- `usage_frequency`
- `support_calls`
- `payment_delay`
- `subscription_type`
- `contract_length`
- `total_spend`
- `last_interaction`
- `created_at`
- `updated_at`

#### `predictions`

Stores prediction results linked to customers:

- `prediction_id`
- `customer_id`
- `predicted_label`
- `churn_probability`
- `model_input_snapshot`
- `recommended_action`
- `created_at`

### API Endpoints

#### Health

- `GET /api/health`

#### Customers

- `GET /api/customers`
- `GET /api/customers/{customer_id}`
- `PUT /api/customers/{customer_id}`
- `GET /api/customers/{customer_id}/predictions`
- `POST /api/customers/{customer_id}/predict`

#### Predictions

- `POST /api/predictions/single`
- `POST /api/predictions/batch`

## Frontend Overview

The frontend is a React application powered by Vite and currently supports three main workflows:

- `Single Prediction`
- `Predict From Database`
- `Batch Prediction`

The client API layer is located in `frontend/src/api/client.js`. By default, the frontend calls the backend through:

```text
http://localhost:8000/api
```

If needed, you can override it with:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## Environment Variables

The project uses a root-level `.env` file. These are the main variables used by the app:

```env
DATABRICKS_URL=
DATABRICKS_TOKEN=
DATABRICKS_TIMEOUT=30

GEMINI_API_KEY=
GEMINI_API_KEYS=
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TIMEOUT=15
FAST_PREDICTION_MODE=false

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=churn_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

PGADMIN_DEFAULT_EMAIL=admin@admin.com
PGADMIN_DEFAULT_PASSWORD=admin

DISABLE_OUTBOUND_PROXY=true
VITE_API_BASE_URL=http://localhost:8000/api
```

### Note About `POSTGRES_HOST`

- When running locally without Docker, use `POSTGRES_HOST=localhost`
- When running with Docker Compose, the `backend` service overrides this to `postgres`

## Run Locally

### 1. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
```

### 3. Start PostgreSQL

You can use a local PostgreSQL instance or start the database services with Docker:

```bash
docker compose up -d postgres pgadmin
```

### 4. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`.

### 5. Start the frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Run With Docker Compose

The project can run the full stack with Docker Compose:

- `postgres`
- `backend`
- `frontend`
- `pgadmin`

### Build and start

```bash
docker compose up --build
```

### Start in detached mode

```bash
docker compose up -d --build
```

### Service URLs

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Health check: `http://localhost:8000/api/health`
- pgAdmin: `http://localhost:5050`
- PostgreSQL: `localhost:5432`

### Stop services

```bash
docker compose down
```

To remove the database volume as well:

```bash
docker compose down -v
```

## Usage

### Single Prediction

Submit one customer profile and receive:

- predicted label
- churn probability
- risk level
- churn drivers
- recommended retention action

### Predict From Database

This workflow allows you to:

- load customers from PostgreSQL
- update customer data before prediction
- run prediction for a stored customer
- persist prediction history in the `predictions` table

### Batch Prediction

Upload a CSV file to run bulk prediction. If the file has missing columns or invalid values, the backend returns validation errors.

You can use [`sample_batch_input.csv`](./sample_batch_input.csv) as a reference file.

## Prediction Lifecycle

1. A user submits customer data from the frontend.
2. FastAPI validates the payload with Pydantic schemas.
3. The service layer transforms the input into model-ready features.
4. The backend sends the scoring request to the Databricks serving endpoint.
5. The result is enriched with analytics and a retention recommendation.
6. For database-backed prediction, the result is stored in PostgreSQL.
7. The frontend renders the final response for review.