from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func
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
        stats.append({
            "id": d.id,
            "code": d.code,
            "title": d.title,
            "priority1": count_p1,
            "priority2": count_p2,
            "priority3": count_p3,
            "total": count_p1 + count_p2 + count_p3
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

@router.post("/campaigns")
def create_campaign(
    name: str,
    start_date: datetime,
    end_date: datetime,
    min_choices: int = 2,
    max_choices: int = 3,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    # Deactivate other campaigns
    session.exec(
        select(Campaign).where(Campaign.active == True)
    ).all() # Just to be safe, we could update them
    
    new_campaign = Campaign(
        name=name,
        start_date=start_date,
        end_date=end_date,
        min_choices=min_choices,
        max_choices=max_choices,
        active=True
    )
    session.add(new_campaign)
    session.commit()
    return new_campaign
