from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from typing import List
from models import Choice, ChoiceSet, User, Campaign
from database import get_session
from routes.auth import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/submit")
def submit_choices(
    discipline_ids: List[int] = Body(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check for active campaign
    campaign = session.exec(select(Campaign).where(Campaign.active == True)).first()
    if not campaign:
        raise HTTPException(status_code=400, detail="No active campaign")
    
    if not (campaign.start_date <= datetime.utcnow() <= campaign.end_date):
        raise HTTPException(status_code=400, detail="Campaign is not currently open")

    if len(discipline_ids) < campaign.min_choices or len(discipline_ids) > campaign.max_choices:
        raise HTTPException(status_code=400, detail=f"Selection must be between {campaign.min_choices} and {campaign.max_choices} items")

    if len(set(discipline_ids)) != len(discipline_ids):
        raise HTTPException(status_code=400, detail="Duplicate disciplines selected")

    # Clear old choices for this campaign
    old_choice_set = session.exec(
        select(ChoiceSet).where(ChoiceSet.user_id == current_user.id, ChoiceSet.campaign_id == campaign.id)
    ).first()
    
    if old_choice_set:
        # Delete old individual choices
        for c in old_choice_set.choices:
            session.delete(c)
        choice_set = old_choice_set
        choice_set.updated_at = datetime.utcnow()
    else:
        choice_set = ChoiceSet(user_id=current_user.id, campaign_id=campaign.id)
    
    session.add(choice_set)
    session.flush()

    # Add new choices with priorities
    for i, d_id in enumerate(discipline_ids):
        choice = Choice(choice_set_id=choice_set.id, discipline_id=d_id, priority=i+1)
        session.add(choice)
    
    session.commit()
    return {"message": "Choices submitted successfully"}

@router.get("/my")
def get_my_choices(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Get active campaign
    campaign = session.exec(select(Campaign).where(Campaign.active == True)).first()
    if not campaign:
        return []

    choice_set = session.exec(
        select(ChoiceSet).where(
            ChoiceSet.user_id == current_user.id,
            ChoiceSet.campaign_id == campaign.id
        )
    ).first()
    
    if not choice_set:
        return []
    
    return [
        {
            "priority": c.priority,
            "discipline": c.discipline
        } for c in sorted(choice_set.choices, key=lambda x: x.priority)
    ]

