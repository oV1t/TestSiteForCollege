from sqlmodel import Session, select, create_engine
import os
from backend.models import User

# Try both SQLite and Postgres if possible
db_url = os.getenv("DATABASE_URL", "sqlite:///elective_disciplines.db")
print(f"Connecting to {db_url}")
engine = create_engine(db_url)

with Session(engine) as session:
    try:
        users = session.exec(select(User)).all()
        for user in users:
            print(f"User: {user.email}, Role: {user.role}")
    except Exception as e:
        print(f"Error: {e}")
