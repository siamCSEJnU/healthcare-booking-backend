from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import users, appointment
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(
    appointment.router, prefix="/api/appointments", tags=["appointments"]
)
