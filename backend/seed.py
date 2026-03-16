from datetime import datetime, timedelta
from sqlmodel import Session, select, SQLModel
from models import Campaign, Discipline, User, UserRole
from database import engine, create_db_and_tables

def seed_data():
    create_db_and_tables()
    with Session(engine) as session:
        # Clear existing data for a fresh start
        session.exec(SQLModel.metadata.tables["choice"].delete())
        session.exec(SQLModel.metadata.tables["choiceset"].delete())
        session.exec(SQLModel.metadata.tables["discipline"].delete())
        session.exec(SQLModel.metadata.tables["campaign"].delete())
        session.exec(SQLModel.metadata.tables["user"].delete())
        session.commit()

        # Create Admin
        admin = User(email="admin@college.edu", full_name="Адміністратор", role=UserRole.ADMIN)
        session.add(admin)

        # Create Campaign
        now = datetime.utcnow()
        campaign = Campaign(
            name="Вибір дисциплін: Весна 2026",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=14),
            min_choices=2,
            max_choices=3,
            active=True
        )
        session.add(campaign)

        # Create Disciplines
        disciplines = [
            Discipline(code="Д-001", title="Розробка веб-застосунків на React", short_info="Сучасний фронтенд на React та TypeScript", doc_url="https://docs.google.com/document/d/web-react"),
            Discipline(code="Д-002", title="Програмування на Python (FastAPI)", short_info="Розробка високонавантажених API", doc_url="https://docs.google.com/document/d/py-fastapi"),
            Discipline(code="Д-003", title="Основи Data Science", short_info="Аналіз даних за допомогою Pandas та Matplotlib", doc_url="https://docs.google.com/document/d/data-science"),
            Discipline(code="Д-004", title="Хмарні технології (AWS/Azure)", short_info="Робота з хмарною інфраструктурою", doc_url="https://docs.google.com/document/d/cloud"),
            Discipline(code="Д-005", title="Мобільна розробка на Flutter", short_info="Створення кросплатформних застосунків", doc_url="https://docs.google.com/document/d/flutter"),
            Discipline(code="Д-006", title="Кібербезпека: Основи", short_info="Захист інформаційних систем від загроз", doc_url="https://docs.google.com/document/d/security"),
            Discipline(code="Д-007", title="Проектування баз даних SQL/NoSQL", short_info="Архітектура та оптимізація сховищ", doc_url="https://docs.google.com/document/d/db-design"),
        ]
        for d in disciplines:
            session.add(d)

        # Create Sample Students
        students = [
            User(email="student1@college.edu", full_name="Іваненко Іван", group_name="КН-21", role=UserRole.STUDENT),
            User(email="student2@college.edu", full_name="Петренко Петро", group_name="КН-21", role=UserRole.STUDENT),
            User(email="student3@college.edu", full_name="Сидоренко Марія", group_name="ПР-32", role=UserRole.STUDENT),
            User(email="student4@college.edu", full_name="Коваленко Олена", group_name="ПР-32", role=UserRole.STUDENT),
            User(email="student5@college.edu", full_name="Бондаренко Андрій", group_name="КС-41", role=UserRole.STUDENT),
        ]
        for s in students:
            session.add(s)

        session.commit()
        print("Database seeded with Ukrainian data successfully")

if __name__ == "__main__":
    seed_data()
