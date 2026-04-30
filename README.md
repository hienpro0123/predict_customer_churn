# 👥 Customer Churn Prediction System

## Overview


A full-stack customer churn prediction application built with FastAPI, React (Vite), Redis, and Databricks Model Serving. The system supports single-customer prediction, prediction from stored Redis customer records, batch CSV scoring, prediction history tracking, and churn-driver analytics.

## System Architecture

<img width="5647" height="3107" alt="Architecture" src="img/flow.jpg" />

## Main Features

- Single-customer churn prediction from a manual form
- Churn prediction for customers stored in Redis
- Prediction history persistence per customer
- Batch prediction from CSV upload
- Churn probability, predicted label, risk level, and churn-driver analytics
- Databricks Model Serving integration for scoring

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
- Pydantic
- Redis
- Uvicorn

### Frontend

- React 18
- Vite
- Fetch API

### External Services

- Databricks Model Serving

## Backend Overview

The backend follows a service-oriented FastAPI structure:

- `routers/`: REST API routes
- `services/`: feature engineering, prediction, analytics, CSV parsing, Databricks, and customer workflows
- `models/`: plain Python domain models for customers and predictions
- `schemas/`: request and response models
- `database/`: Redis client wiring
- `core/`: application settings loaded from `.env`
- `utils/`: shared constants and helper utilities

### Redis Keys

#### `customer:{customer_id}`

Stores customer input data used for Redis-backed prediction:

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

#### `prediction_history:{customer_id}`

Stores prediction results linked to customers:

- `prediction_id`
- `customer_id`
- `predicted_label`
- `churn_probability`
- `model_input_snapshot`
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

REDIS_HOST=
REDIS_PORT=6379
REDIS_USERNAME=default
REDIS_PASSWORD=
REDIS_DB=0

DISABLE_OUTBOUND_PROXY=true
VITE_API_BASE_URL=http://localhost:8000/api
```

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

### 3. Start the backend

```bash
cd backend
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`.

### 4. Start the frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Run With Docker Compose

The project can run the app stack with Docker Compose:

- `backend`
- `frontend`

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

### Stop services

```bash
docker compose down
```

## Usage

### Single Prediction

Submit one customer profile and receive:

- predicted label
- churn probability
- risk level
- churn drivers

### Predict From Stored Customers

This workflow allows you to:

- load customers from Redis
- update customer data before prediction
- run prediction for a stored customer
- persist prediction history in Redis

### Batch Prediction

Upload a CSV file to run bulk prediction. If the file has missing columns or invalid values, the backend returns validation errors.

You can use [`sample_batch_input.csv`](./sample_batch_input.csv) as a reference file.

## Prediction Lifecycle

1. A user submits customer data from the frontend.
2. FastAPI validates the payload with Pydantic schemas.
3. The service layer transforms the input into model-ready features.
4. The backend sends the scoring request to the Databricks serving endpoint.
5. The result is enriched with churn analytics.
6. For stored-customer prediction, the result is stored in Redis.
7. The frontend renders the final response for review.
