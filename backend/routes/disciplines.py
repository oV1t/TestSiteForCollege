from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from models import Discipline
from database import get_session
from routes.auth import get_current_user

router = APIRouter()

@router.get("/")
def list_disciplines(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    return session.exec(select(Discipline).where(Discipline.active == True)).all()

@router.get("/{discipline_id}")
def get_discipline(
    discipline_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    return session.get(Discipline, discipline_id)
