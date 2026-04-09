from fastapi import FastAPI
from app.api.research import router as research_router
from app.api.health import router as health_router
from app.core.logger import logger

app = FastAPI(
    title="YouTube Research Agent",
    version="0.1.0",
    description="AI-powered YouTube channel research agent",
)

app.include_router(research_router, prefix="/api/v1")
app.include_router(health_router)


@app.on_event("startup")
async def startup():
    logger.info("app_started")


@app.on_event("shutdown")
async def shutdown():
    logger.info("app_stopped")