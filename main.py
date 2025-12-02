from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, user
from app.models import Base
from app.utils.database import engine


app = FastAPI(title="Exit Prep", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(user.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "EduGG API is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EduGG Backend"}

@app.on_event("startup")
def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
