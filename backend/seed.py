from datetime import datetime, timedelta
from sqlmodel import Session, select, SQLModel
from models import Campaign, Discipline, User, UserRole
from database import engine, create_db_and_tables
from routes.auth import get_password_hash

def seed_data():
    create_db_and_tables()
    with Session(engine) as session:
        # Clear existing data for a fresh start safely
        for table in reversed(SQLModel.metadata.sorted_tables):
            try:
                session.exec(table.delete())
            except Exception as e:
                print(f"Skipping detailed delete for {table.name}: {e}")
        session.commit()

        # Create Admin
        admin = User(
            email="admin@college.edu", 
            full_name="Адміністратор", 
            role=UserRole.ADMIN,
            hashed_password=get_password_hash("admin123")
        )
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
        Discipline(code="ВК-1", title="Етика ділового спілкування іноземною мовою / Business communication in a foreign language", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/1"),
        Discipline(code="ВК-2", title="Реклама та PR-технології / Advertising and PR technologies", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/2"),
        Discipline(code="ВК-3", title="Основи гостинності в сфері туристичного обслуговування / Fundamentals of hospitality in the field of tourist services", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/3"),
        Discipline(code="ВК-4", title="Діловий етикет і протокол в туризмі / Business etiquette of a tourism organization", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/4"),
        Discipline(code="ВК-5", title="Музеєзнавство та культурна спадщина в туризмі / Museology and Interpretation", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/5"),
        Discipline(code="ВК-6", title="Гастрономічний туризм та кулінарні традиції країн світу / Gastronomic tourism and culinary traditions of the world", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/6"),
        Discipline(code="ВК-7", title="Страхові послуги в туризмі / Insurance services in tourism", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/7"),
        Discipline(code="ВК-8", title="Правове регулювання туристичної діяльності / Legal regulation of tourism activity", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/8"),
        Discipline(code="ВК-9", title="Безпека туристичної діяльності / Tourism, Security and Safety", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/9"),
        Discipline(code="ВК-10", title="Туроперейтинг / Tour Operating", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/10"),
        Discipline(code="ВК-11", title="Облік і оподаткування підприємств малого бізнесу / Accounting and taxation for small businesses", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/11"),
        Discipline(code="ВК-12", title="Облік і аналіз ЗЕД / Accounting and analysis of foreign economic activity", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/12"),
        Discipline(code="ВК-13", title="Фінансовий менеджмент / Financial management", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/13"),
        Discipline(code="ВК-14", title="Управлінський облік / Management Accounting", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/14"),
        Discipline(code="ВК-15", title="Гроші і кредит / Money and credit", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/15"),
        Discipline(code="ВК-16", title="Ціноутворення / Pricing", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/16"),
        Discipline(code="ВК-17", title="Облікова політика підприємства / Accounting policy of the enterprise", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/17"),
        Discipline(code="ВК-18", title="Звітність підприємств / Enterprise reporting", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/18"),
        Discipline(code="ВК-19", title="Організація біржової діяльності / Organization of stock exchange activities", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/19"),
        Discipline(code="ВК-20", title="Організація бізнесу та інвестування / Business organization and investment", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/20"),
        Discipline(code="ВК-21", title="Фінансово-економічний аналіз / Financial and economic analysis", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/21"),
        Discipline(code="ВК-22", title="Основи фінансової грамотності / Fundamentals of Financial Literacy", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/22"),
        Discipline(code="ВК-23", title="Логістика / Logistics", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/23"),
        Discipline(code="ВК-24", title="Фінансовий ринок / Financial market", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/24"),
        Discipline(code="ВК-25", title="Трудове право / Labor law", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/25"),
        Discipline(code="ВК-26", title="Основи стандартизації, метрології та управління якістю / Basics of standardization, metrology and quality management", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/26"),
        Discipline(code="ВК-27", title="Господарське право / Commercial law", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/27"),
        Discipline(code="ВК-28", title="Зовнішньоекономічна діяльність / Foreign Economic Activity", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/28"),
        Discipline(code="ВК-29", title="Основи екології та безпеки товарів народного споживання / Fundamentals of ecology and safety of consumer goods consumption", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/29"),
        Discipline(code="ВК-30", title="Проєктування торговельних обєктів / Retail Design", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/30"),
        Discipline(code="ВК-31", title="Лідерство / Leadership", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/31"),
        Discipline(code="ВК-32", title="Менеджмент у продуктовому ІТ / Management in product IT", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/32"),
        Discipline(code="ВК-33", title="Матеріалознавство / Materials science", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/33"),
        Discipline(code="ВК-34", title="Тара та пакувальні матеріали / Packaging & Containers", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/34"),
        Discipline(code="ВК-35", title="Інфраструктура товарного ринку", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/35"),
        Discipline(code="ВК-36", title="Експертиза товарів народного споживання", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/36"),
        Discipline(code="ВК-37", title="Фінанси підприємства", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/37"),
        Discipline(code="ВК-38", title="Страхування", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/38"),
        Discipline(code="ВК-39", title="Барна справа", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/39"),
        Discipline(code="ВК-40", title="Екологія харчових виробництв", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/40"),
        Discipline(code="ВК-41", title="Крафтові технології", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/41"),
        Discipline(code="ВК-42", title="Інноваційні ресторанні технології", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/42"),
        Discipline(code="ВК-43", title="Українська кухня", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/43"),
        Discipline(code="ВК-44", title="Основи еногастрономії", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/44"),
        Discipline(code="ВК-45", title="Кулінарні традиції країн світу", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/45"),
        Discipline(code="ВК-46", title="Технологія продукції дієтичного харчування", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/46"),
        Discipline(code="ВК-47", title="Практикум з технології продукції ресторанного господарства", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/47"),
        Discipline(code="ВК-48", title="Мистецтво сомельє", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/48"),
        Discipline(code="ВК-49", title="Інноваційні та екобезпечні пакувальні матеріали для харчових продуктів", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/49"),
        Discipline(code="ВК-50", title="Товарознавство харчових продуктів", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/50"),
        Discipline(code="ВК-51", title="Інноваційний інжиніринг закладів ресторанного господарства", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/51"),
        Discipline(code="ВК-52", title="Міжнародна готельна індустрія", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/52"),
        Discipline(code="ВК-53", title="Кулінарні традиції країн світу", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/53"),
        Discipline(code="ВК-54", title="Основи сервісу", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/54"),
        Discipline(code="ВК-55", title="Іміджологія та бренд-менеджмент в готельно-ресторанній справі", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/55"),
        Discipline(code="ВК-56", title="Естетичне оформлення готелів", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/56"),
        Discipline(code="ВК-57", title="Будівлі та обладнання готелів", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/57"),
        Discipline(code="ВК-58", title="Інноваційні ресторанні технології", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/58"),
        Discipline(code="ВК-59", title="Хмарні технології та сервіси", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/59"),
        Discipline(code="ВК-60", title="Інженерна графіка", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/60"),
        Discipline(code="ВК-61", title="Офісне програмне забезпечення", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/61"),
        Discipline(code="ВК-62", title="Програмування для мобільних платформ", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/62"),
        Discipline(code="ВК-63", title="Комп’ютерні та мікропроцесорні системи, організація комп'ютерних мереж", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/63"),
        Discipline(code="ВК-64", title="Програмування комп’ютерних ігор", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/64"),
        Discipline(code="ВК-65", title="Основи інтернету речей та програмування пристроїв", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/65"),
        Discipline(code="ВК-66", title="Геймдизайн та програмування ігрових застосунків", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/66"),
        Discipline(code="ВК-67", title="Штучний інтелект та методи машинного навчання", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/67"),
        Discipline(code="ВК-68", title="Архітектура програмних систем", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/68"),
        Discipline(code="ВК-69", title="Статистичні методи аналізу даних", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/69"),
        Discipline(code="ВК-70", title="Компонентно-орієнтоване програмування", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/70"),
        Discipline(code="ВК-71", title="Дата інженерія та опрацювання даних", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/71"),
        Discipline(code="ВК-72", title="Основи психології та етика ділових відносин", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/72"),
        Discipline(code="ВК-73", title="Друга іноземна мова (польська)", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/73"),
        Discipline(code="ВК-74", title="Сучасне красномовство", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/74"),
        Discipline(code="ВК-75", title="Сучасні способи переробки органічної сировини різного походження", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/75"),
        Discipline(code="ВК-76", title="Криптовалюти та віртуальні біржі", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/76"),
        Discipline(code="ВК-77", title="Управління персоналом", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/77"),
        Discipline(code="ВК-78", title="Грошово-кредитна політика", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/78"),
        Discipline(code="ВК-79", title="Органічні харчові продукти спеціального призначення", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/79"),
        Discipline(code="ВК-80", title="Регулювання використання харчових добавок в різних технологіях", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/80"),
        Discipline(code="ВК-81", title="Цифрові технології в харчовій галузі", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/81"),
        Discipline(code="ВК-82", title="Фінансова грамотність", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/82"),
        Discipline(code="ВК-83", title="Компанія", short_info="Дисципліна за вибором", doc_url="https://docs.google.com/document/d/83"),            
       ]
        for d in disciplines:
            session.add(d)

        # Create Sample Students
        default_password = get_password_hash("password123")
        students = [
            User(email="student1@college.edu", full_name="Іваненко Іван", group_name="КН-21", role=UserRole.STUDENT, hashed_password=default_password),
            User(email="student2@college.edu", full_name="Петренко Петро", group_name="КН-21", role=UserRole.STUDENT, hashed_password=default_password),
            User(email="student3@college.edu", full_name="Сидоренко Марія", group_name="ПР-32", role=UserRole.STUDENT, hashed_password=default_password),
            User(email="student4@college.edu", full_name="Коваленко Олена", group_name="ПР-32", role=UserRole.STUDENT, hashed_password=default_password),
            User(email="student5@college.edu", full_name="Бондаренко Андрій", group_name="КС-41", role=UserRole.STUDENT, hashed_password=default_password),
        ]
        for s in students:
            session.add(s)

        session.commit()
        print("Database seeded with Ukrainian data successfully")

if __name__ == "__main__":
    seed_data()
