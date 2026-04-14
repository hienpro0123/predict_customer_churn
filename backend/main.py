from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from database.init_db import init_db
from routers.customers import router as customers_router
from routers.health import router as health_router
from routers.predictions import router as predictions_router
app = FastAPI(title="Customer Churn API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health_router, prefix="/api")
app.include_router(customers_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
