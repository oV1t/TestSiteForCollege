from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select
from typing import List
from models import Choice, ChoiceSet, User, Campaign
from database import get_session
from routes.auth import get_current_user
from datetime import datetime, timezone

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

    # Ensure all datetimes are compared as naive UTC to avoid timezone issues
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    start_date = campaign.start_date.replace(tzinfo=None)
    end_date = campaign.end_date.replace(tzinfo=None)

    # Date range check removed as per user request
    # if not (start_date <= now <= end_date):
    #     raise HTTPException(
    #         status_code=400, 
    #         detail=f"Період вибору не активний. Поточний час: {now.strftime('%Y-%m-%d %H:%M')}, "
    #                f"Початок: {start_date.strftime('%Y-%m-%d %H:%M')}, "
    #                f"Кінець: {end_date.strftime('%Y-%m-%d %H:%M')}"
    #     )

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
        choice_set.updated_at = datetime.now(timezone.utc)
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

