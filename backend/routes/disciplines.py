from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from models import Discipline, Choice
from database import get_session
from routes.auth import get_current_user

router = APIRouter()

@router.get("/")
def list_disciplines(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    # Fetch all active disciplines with natural sorting
    disciplines_stmt = select(Discipline).where(Discipline.active == True).order_by(func.length(Discipline.code), Discipline.code)
    disciplines = session.exec(disciplines_stmt).all()
    
    # Calculate choice count for each discipline
    results = []
    for d in disciplines:
        count = session.exec(select(func.count(Choice.id)).where(Choice.discipline_id == d.id)).one()
        d_dict = d.model_dump()
        d_dict["choice_count"] = count
        results.append(d_dict)
        
    return results

@router.get("/{discipline_id}")
def get_discipline(
    discipline_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    return session.get(Discipline, discipline_id)
