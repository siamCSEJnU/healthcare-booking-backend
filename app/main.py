from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import users

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(users.router, prefix="/api/users", tags=["Users"])
