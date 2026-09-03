from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    ai_assistant,
    alerts,
    auth,
    dashboard,
    financial_health,
    loans,
    recommendations,
    risk,
    scenarios,
    transactions,
)
from app.core.config import get_settings
from app.database.connection import init_db

settings = get_settings()

app = FastAPI(
    title="FinGuard AI API",
    description=(
        "FinGuard AI — AI-Powered Early Financial Distress Prevention System. "
        "Prevention, not punishment."
    ),
    version=settings.APP_VERSION,
)

# CORS - allow configured frontend origins
origins = settings.BACKEND_CORS_ORIGINS
if settings.FRONTEND_URL and settings.FRONTEND_URL not in origins:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    # Seed demo customer(s) so the app works out of the box.
    if settings.AUTO_SEED:
        from app.database.seed import seed_demo_data
        seed_demo_data()


# Health check
@app.get("/api/health", tags=["System"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# Include API routers under /api
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(financial_health.router, prefix="/api")
app.include_router(risk.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(ai_assistant.router, prefix="/api")
app.include_router(scenarios.router, prefix="/api")
