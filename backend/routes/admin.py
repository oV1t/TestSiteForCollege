from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func, SQLModel
from sqlalchemy.exc import IntegrityError
from typing import List
import io
import csv
from datetime import datetime
from models import Choice, ChoiceSet, User, Discipline, UserRole, Campaign
from database import get_session
from routes.auth import require_admin

router = APIRouter()

@router.get("/stats")
def get_stats(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    # Total students who made a choice
    total_participants = session.exec(select(func.count(ChoiceSet.id))).one()
    
    # Discipline popularity
    disciplines = session.exec(select(Discipline)).all()
    stats = []
    for d in disciplines:
        count_p1 = session.exec(select(func.count(Choice.id)).where(Choice.discipline_id == d.id, Choice.priority == 1)).one()
        count_p2 = session.exec(select(func.count(Choice.id)).where(Choice.discipline_id == d.id, Choice.priority == 2)).one()
        count_p3 = session.exec(select(func.count(Choice.id)).where(Choice.discipline_id == d.id, Choice.priority == 3)).one()
        
        # New: Group breakdown (Total for all priorities)
        group_counts = session.exec(
            select(User.group_name, func.count(Choice.id))
            .join(ChoiceSet, ChoiceSet.user_id == User.id)
            .join(Choice, Choice.choice_set_id == ChoiceSet.id)
            .where(Choice.discipline_id == d.id)
            .group_by(User.group_name)
        ).all()
        
        group_stats = [{"group": g, "count": c} for g, c in group_counts if g]
        stats.append({
            "id": d.id,
            "code": d.code,
            "title": d.title,
            "priority1": count_p1,
            "priority2": count_p2,
            "priority3": count_p3,
            "total": count_p1 + count_p2 + count_p3,
            "group_stats": group_stats
        })
    
    return {
        "total_participants": total_participants,
        "discipline_stats": stats
    }

@router.get("/export/csv")
def export_choices_csv(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Email", "Full Name", "Group", "Priority 1", "Priority 2", "Priority 3", "Submitted At"])
    
    choicesets = session.exec(select(ChoiceSet)).all()
    for cs in choicesets:
        p1 = next((c.discipline.title for c in cs.choices if c.priority == 1), "")
        p2 = next((c.discipline.title for c in cs.choices if c.priority == 2), "")
        p3 = next((c.discipline.title for c in cs.choices if c.priority == 3), "")
        writer.writerow([
            cs.user.email,
            cs.user.full_name,
            cs.user.group_name,
            p1, p2, p3,
            cs.submitted_at.isoformat()
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=elective_choices.csv"}
    )

from pydantic import BaseModel
from typing import Optional

class DisciplineCreate(BaseModel):
    code: str
    title: str
    short_info: Optional[str] = None
    doc_url: Optional[str] = None
    active: bool = True

class DisciplineUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    short_info: Optional[str] = None
    doc_url: Optional[str] = None
    active: Optional[bool] = None

@router.get("/disciplines", response_model=List[Discipline])
def get_all_disciplines(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    return session.exec(select(Discipline)).all()

@router.post("/disciplines", response_model=Discipline)
def create_discipline(
    data: DisciplineCreate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    new_discipline = Discipline(**data.model_dump())
    session.add(new_discipline)
    session.commit()
    session.refresh(new_discipline)
    return new_discipline

@router.put("/disciplines/{discipline_id}", response_model=Discipline)
def update_discipline(
    discipline_id: int,
    data: DisciplineUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    discipline = session.get(Discipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(discipline, key, value)
    
    discipline.updated_at = datetime.utcnow()
    session.add(discipline)
    session.commit()
    session.refresh(discipline)
    return discipline

@router.delete("/disciplines/{discipline_id}")
def delete_discipline(
    discipline_id: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    discipline = session.get(Discipline, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    try:
        session.delete(discipline)
        session.commit()
        return {"ok": True, "message": "Discipline deleted successfully"}
    except IntegrityError:
        session.rollback()
        # Fallback to soft delete
        discipline.active = False
        session.add(discipline)
        session.commit()
        return {"ok": True, "message": "Discipline deactivated (cannot be deleted due to existing student choices)"}

@router.post("/choices/clear")
def clear_all_choices(
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    try:
        session.exec(SQLModel.metadata.tables["choice"].delete())
        session.exec(SQLModel.metadata.tables["choiceset"].delete())
        session.commit()
        return {"ok": True, "message": "All student choices have been cleared"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

