from fastapi import FastAPI
from contextlib import asynccontextmanager

from configs.config import PROJECT_NAME, PROJECT_VERSION
from db.session import engine, Base
from routes.route import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Warning: Could not create tables on startup: {e}")
        print("Tables will be created on first successful connection.")
    yield


def start_application():
    app = FastAPI(title=PROJECT_NAME, version=PROJECT_VERSION, lifespan=lifespan)
    app.include_router(router)
    return app


app = start_application()