from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import create_tables
from app.routers import applications, features, listings, messages, persons, recommendations, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="CrowdApply API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(listings.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(applications.router, prefix="/api")
app.include_router(features.router, prefix="/api")
app.include_router(persons.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
