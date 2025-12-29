from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import engine, Base
from app.api.v1 import auth, venues, songs, bookings, sessions, suggestions
from fastapi.staticfiles import StaticFiles

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(venues.router, prefix=f"{settings.API_V1_PREFIX}/venues", tags=["Venues"])
app.include_router(songs.router, prefix=f"{settings.API_V1_PREFIX}/songs", tags=["Songs"])
app.include_router(bookings.router, prefix=f"{settings.API_V1_PREFIX}/bookings", tags=["Bookings"])
app.include_router(sessions.router, prefix=f"{settings.API_V1_PREFIX}/sessions", tags=["Sessions"])
app.include_router(suggestions.router, prefix=f"{settings.API_V1_PREFIX}/suggestions", tags=["Suggestions"])
# app.include_router(chat.router, tags=["Chat"])

@app.get("/")
def root():
    return {
        "message": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}