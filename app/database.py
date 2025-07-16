from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("LOCAL_DATABASE_URL")
# print(f"✅ Using DB: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
