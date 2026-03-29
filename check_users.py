from sqlmodel import Session, select, create_engine
from backend.models import User

engine = create_engine("sqlite:///elective_disciplines.db")

with Session(engine) as session:
    users = session.exec(select(User)).all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Role: {user.role}")
