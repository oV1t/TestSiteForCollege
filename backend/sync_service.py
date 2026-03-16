import pandas as pd
from datetime import date, datetime
from typing import List
from sqlmodel import Session, select
from models import Discipline, SyncState
from database import engine

# This is a placeholder for actual Google Sheets API integration
# In a real scenario, you would use google-auth and google-api-python-client

def sync_disciplines_from_sheet(sheet_url: str):
    """
    Synchronizes disciplines from a Google Sheet.
    Expects columns: code, title, short_info, doc_url, active
    """
    # For MVP, we might use a direct CSV export URL or a service account
    # CSV export URL format: https://docs.google.com/spreadsheets/d/{ID}/export?format=csv
    
    try:
        df = pd.read_csv(sheet_url)
        
        with Session(engine) as session:
            # Check if synced today
            state = session.get(SyncState, 1)
            if state and state.last_synced_date == date.today():
                return "Already synced today"

            for _, row in df.iterrows():
                discipline = session.exec(
                    select(Discipline).where(Discipline.code == row['code'])
                ).first()
                
                if discipline:
                    discipline.title = row['title']
                    discipline.short_info = row.get('short_info')
                    discipline.doc_url = row.get('doc_url')
                    discipline.active = bool(row.get('active', True))
                    discipline.updated_at = datetime.utcnow()
                    session.add(discipline)
                else:
                    new_discipline = Discipline(
                        code=row['code'],
                        title=row['title'],
                        short_info=row.get('short_info'),
                        doc_url=row.get('doc_url'),
                        active=bool(row.get('active', True))
                    )
                    session.add(new_discipline)

            # Update sync state
            if not state:
                state = SyncState(id=1, last_synced_date=date.today(), last_sync_status="success")
            else:
                state.last_synced_date = date.today()
                state.last_sync_status = "success"
            
            session.add(state)
            session.commit()
            return "Sync successful"
            
    except Exception as e:
        with Session(engine) as session:
            state = session.get(SyncState, 1)
            if not state:
                state = SyncState(id=1, last_synced_date=date.today(), last_sync_status="error", last_error=str(e))
            else:
                state.last_sync_status = "error"
                state.last_error = str(e)
            session.add(state)
            session.commit()
        raise e
