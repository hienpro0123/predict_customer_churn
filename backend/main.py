from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from routers.customers import router as customers_router
from routers.health import router as health_router
from routers.predictions import router as predictions_router


app = FastAPI(title="Customer Churn API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router, prefix="/api")
app.include_router(customers_router, prefix="/api")
app.include_router(predictions_router, prefix="/api")
