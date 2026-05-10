from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func, SQLModel
from sqlalchemy.exc import IntegrityError
from typing import List
import io
import csv
from datetime import datetime, timezone
import pandas as pd
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
        
        # New: Group breakdown (Total for all priorities) with student names
        choices_data = session.exec(
            select(User.full_name, User.group_name, ChoiceSet.submitted_at)
            .join(ChoiceSet, ChoiceSet.user_id == User.id)
            .join(Choice, Choice.choice_set_id == ChoiceSet.id)
            .where(Choice.discipline_id == d.id)
            .order_by(User.group_name, User.full_name)
        ).all()
        
        group_map = {}
        for name, group, submitted_at in choices_data:
            if not group: continue
            if group not in group_map:
                group_map[group] = []
            group_map[group].append({
                "full_name": name,
                "year": submitted_at.year if submitted_at else datetime.now().year
            })
        
        group_stats = [
            {"group": g, "count": len(s), "students": s} 
            for g, s in group_map.items()
        ]
        stats.append({
            "id": d.id,
            "code": d.code,
            "title": d.title,
            "commission_name": d.commission_name,
            "specialty_code": d.specialty_code,
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

@router.get("/export/xlsx")
def export_choices_xlsx(
    year: int,
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    # Filter by year from submitted_at
    choicesets = session.exec(
        select(ChoiceSet)
        .where(func.extract('year', ChoiceSet.submitted_at) == year)
    ).all()
    
    data = []
    for cs in choicesets:
        p1 = next((c.discipline.title for c in cs.choices if c.priority == 1), "")
        p2 = next((c.discipline.title for c in cs.choices if c.priority == 2), "")
        p3 = next((c.discipline.title for c in cs.choices if c.priority == 3), "")
        data.append({
            "Email": cs.user.email,
            "Full Name": cs.user.full_name,
            "Group": cs.user.group_name,
            "Priority 1": p1,
            "Priority 2": p2,
            "Priority 3": p3,
            "Submitted At": cs.submitted_at.replace(tzinfo=None) if cs.submitted_at else None
        })
    
    df = pd.DataFrame(data)
    
    # Generate Excel in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Choices {year}')
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=elective_choices_{year}.xlsx"}
    )

from pydantic import BaseModel
from typing import Optional

class DisciplineCreate(BaseModel):
    code: str
    title: str
    short_info: Optional[str] = None
    doc_url: Optional[str] = None
    commission_name: Optional[str] = None
    specialty_code: Optional[str] = None
    credits: Optional[float] = None
    teacher_name: Optional[str] = None
    competence_type: Optional[str] = None
    active: bool = True

class DisciplineUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None
    short_info: Optional[str] = None
    doc_url: Optional[str] = None
    commission_name: Optional[str] = None
    specialty_code: Optional[str] = None
    credits: Optional[float] = None
    teacher_name: Optional[str] = None
    competence_type: Optional[str] = None
    active: Optional[bool] = None

@router.get("/disciplines")
async def get_admin_disciplines(session: Session = Depends(get_session), admin: User = Depends(require_admin)):
    return session.exec(select(Discipline).order_by(func.length(Discipline.code), Discipline.code)).all()

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
    
    discipline.updated_at = datetime.now(timezone.utc)
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



from fastapi import UploadFile, File
import io

@router.post("/disciplines/import")
async def import_disciplines(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    admin: User = Depends(require_admin)
):
    try:
        content = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            # For Excel, we might want to extract hyperlinks
            from openpyxl import load_workbook
            wb = load_workbook(io.BytesIO(content), data_only=False)
            ws = wb.active
            df = pd.read_excel(io.BytesIO(content))
        
        # mapping based on keywords to be more robust
        def get_col_name(cols, keywords):
            for col in cols:
                if not col or pd.isna(col): continue
                # Remove spaces and newlines for comparison
                clean_col = "".join(str(col).lower().split())
                if all("".join(k.lower().split()) in clean_col for k in keywords):
                    return col
            return None

        # Try to find the header row if the first one isn't it
        header_index = 0
        current_cols = list(df.columns)
        
        # Check if current headers are valid
        if not (get_col_name(current_cols, ["Код", "ВК"]) and get_col_name(current_cols, ["Назва", "дисциплін"])):
            # If not, scan first 10 rows to find headers
            found = False
            # Read without header to scan rows accurately
            df_source = pd.read_excel(io.BytesIO(content), header=None) if not file.filename.endswith('.csv') else pd.read_csv(io.BytesIO(content), header=None)
            
            for i in range(min(10, len(df_source))):
                row_values = df_source.iloc[i].tolist()
                if get_col_name(row_values, ["Код", "ВК"]) and get_col_name(row_values, ["Назва", "дисциплін"]):
                    # Found it! Header is row 'i', data starts at 'i+1'
                    header_index = i
                    # Use this source and set columns manually
                    headers = [str(col).strip() if not pd.isna(col) else f"Unnamed_{idx}" for idx, col in enumerate(row_values)]
                    df = df_source.iloc[i+1:].reset_index(drop=True)
                    df.columns = headers
                    if not file.filename.endswith('.csv'):
                        # Already loaded workbook above as 'wb', we'll use it
                        pass 
                    found = True
                    break
            
            if not found:
                raise HTTPException(status_code=400, detail=f"Не вдалося знайти рядок із заголовками (Код та Назва). Знайдено лише: {list(df.columns[:3])}...")
        else:
            # First row was actually headers, but we might still need openpyxl ws
            pass

        # Detect columns from final headers
        final_cols = list(df.columns)
        code_col = get_col_name(final_cols, ["Код", "ВК"]) or get_col_name(final_cols, ["Код"]) or get_col_name(final_cols, ["Code"])
        title_col = get_col_name(final_cols, ["Назва", "дисциплін"]) or get_col_name(final_cols, ["Назва"]) or get_col_name(final_cols, ["Title"])
        credits_col = get_col_name(final_cols, ["кредит"]) or get_col_name(final_cols, ["Credits"])
        teacher_col = get_col_name(final_cols, ["викладач"]) or get_col_name(final_cols, ["Teacher"])
        comp_col = get_col_name(final_cols, ["компетентност"]) or get_col_name(final_cols, ["Competence"])
        comm_col = get_col_name(final_cols, ["коміс"]) or get_col_name(final_cols, ["ЦК"]) or get_col_name(final_cols, ["Commission"])
        spec_col = get_col_name(final_cols, ["спеціальн"]) or get_col_name(final_cols, ["шифр"]) or get_col_name(final_cols, ["Specialty"])
        
        # URL column search: any of these keywords (aggressive search)
        url_col = None
        url_col_idx = -1
        for idx, col in enumerate(final_cols):
            c = str(col).lower()
            if any(k in c for k in ["диск", "disk", "google", "посилання", "силабус", "папк", "матеріал", "докум", "url"]):
                url_col = col
                url_col_idx = idx
                break

        print(f"IMPORT DEBUG: Final Map: code={code_col}, title={title_col}, teacher={teacher_col}, credits={credits_col}, url={url_col}, comm={comm_col}, spec={spec_col}")

        def normalize_code(c):
            if not c or pd.isna(c): return ""
            # Replace common Latin lookalikes with Cyrillic and normalize dashes
            s = str(c).strip().upper()
            s = s.replace("V", "В").replace("B", "В").replace("K", "К").replace("–", "-").replace("—", "-")
            return s

        stats = {"created": 0, "updated": 0}
        last_comm = None
        last_spec = None
        
        for index, row in df.iterrows():
            # Update sticky categories if new values are found in this row
            raw_comm = row.get(comm_col)
            if comm_col and not pd.isna(raw_comm) and str(raw_comm).strip():
                last_comm = str(raw_comm).strip()
                
            raw_spec = row.get(spec_col)
            if spec_col and not pd.isna(raw_spec) and str(raw_spec).strip():
                last_spec = str(raw_spec).strip()

            raw_code = row.get(code_col)
            if pd.isna(raw_code) or pd.isna(row.get(title_col)):
                continue
                
            code = normalize_code(raw_code)
            # Skip if it's just the header or empty
            if not code or code in ["КОД", "КОДОСВІТНЬОГОКОМПОНЕНТА"]:
                continue

            # Normalized search in DB
            all_disciplines = session.exec(select(Discipline)).all()
            discipline = next((d for d in all_disciplines if normalize_code(d.code) == code), None)

            # TRY TO EXTRACT HYPERLINK IF EXCEL
            extracted_url = None
            if not file.filename.endswith('.csv') and url_col_idx != -1:
                try:
                    # openpyxl uses 1-based indexing
                    # header_index is where headers are. rows below are data.
                    # row index starts from 0 in iterrows, so it's data row.
                    # Excel row = header_index + 1 (for header) + index + 1
                    excel_row = header_index + 2 + index 
                    ws_row = list(ws.rows)[excel_row - 1]
                    cell = ws_row[url_col_idx]
                    if cell.hyperlink:
                        extracted_url = cell.hyperlink.target
                except:
                    pass

            doc_url = extracted_url or (str(row[url_col]).strip() if url_col and not pd.isna(row.get(url_col)) else None)
            
            def safe_float(val):
                if pd.isna(val) or val is None: return None
                try:
                    # Remove non-numeric characters except dot/comma
                    s = "".join(c for c in str(val) if c.isdigit() or c in ".,")
                    return float(s.replace(",", "."))
                except:
                    return None

            data = {
                "title": str(row[title_col]).strip(),
                "short_info": str(row.get('short_info', '')) if not pd.isna(row.get('short_info')) else None,
                "doc_url": doc_url,
                "commission_name": last_comm,
                "spec": last_spec,
                "credits": safe_float(row.get(credits_col)),
                "teacher": str(row[teacher_col]).strip() if teacher_col and not pd.isna(row.get(teacher_col)) else None,
                "ctype": str(row[comp_col]).strip() if comp_col and not pd.isna(row.get(comp_col)) else None,
            }
            
            if discipline:
                discipline.title = data["title"]
                discipline.doc_url = data["doc_url"]
                discipline.commission_name = data["commission_name"]
                discipline.specialty_code = data["spec"]
                discipline.credits = data["credits"]
                discipline.teacher_name = data["teacher"]
                discipline.competence_type = data["ctype"]
                discipline.updated_at = datetime.now(timezone.utc)
                stats["updated"] += 1
            else:
                new_disc = Discipline(
                    code=code, 
                    title=data["title"],
                    doc_url=data["doc_url"],
                    commission_name=data["commission_name"],
                    specialty_code=data["spec"],
                    credits=data["credits"],
                    teacher_name=data["teacher"],
                    competence_type=data["ctype"],
                    active=True
                )
                session.add(new_disc)
                stats["created"] += 1
                
        session.commit()
        return {"ok": True, "message": f"Імпорт завершено: створено {stats['created']}, оновлено {stats['updated']}"}
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Помилка імпорту: {str(e)}")

