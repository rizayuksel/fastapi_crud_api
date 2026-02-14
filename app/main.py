from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 {settings.APP_NAME} starting...")
    await init_db()
    print("✅ Database ready!")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI CRUD API with PostgreSQL and JWT",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
async def root():
    return {"status": "ok", "message": "FastAPI CRUD API is running", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
