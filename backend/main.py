from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routes import auth, disciplines, choices, admin

app = FastAPI(title="Elective Disciplines Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(disciplines.router, prefix="/api/disciplines", tags=["disciplines"])
app.include_router(choices.router, prefix="/api/choices", tags=["choices"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Elective Disciplines API is running"}
