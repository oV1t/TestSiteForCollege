from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from sqlmodel import Session, select
from models import User, UserRole
from database import get_session
from passlib.context import CryptContext
from google_api import google_admin
from google.oauth2 import id_token
from google.auth.transport import requests
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-dev")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin role required")
    return current_user

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний email або пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": str(user.role.value if hasattr(user.role, 'value') else user.role)}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    user_data = current_user.model_dump(exclude={"hashed_password"})
    user_data["role"] = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role)
    return user_data

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    group_name: Optional[str] = None

@router.put("/me")
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.group_name is not None:
        current_user.group_name = user_update.group_name
    
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

class GoogleVerifyRequest(BaseModel):
    token: str

@router.post("/google-verify")
async def google_verify(
    request: GoogleVerifyRequest,
    session: Session = Depends(get_session)
):
    try:
        # Verify the ID token from Google
        idinfo = id_token.verify_oauth2_token(
            request.token, 
            requests.Request(), 
            os.getenv("GOOGLE_CLIENT_ID")
        )

        # ID token is valid. Extract info.
        email = idinfo['email']
        # Google returns 'name' as full name
        google_name = idinfo.get('name', 'Google User')
        
    except ValueError:
        # Invalid token
        raise HTTPException(status_code=401, detail="Invalid Google token")

    # Verify domain
    if not email.endswith("@rcit.ukr.education"):
        raise HTTPException(status_code=403, detail="Дозволено вхід тільки з корпоративною поштою @rcit.ukr.education")

    # Fetch info from Google Admin Directory
    google_fullname, department, org_unit = google_admin.get_user_info(email)
    
    # Prioritize name from verified token, fallback to Admin API
    final_name = google_name or google_fullname or "Google User"

    # Use department (Group) or Fallback to OrgUnit if department is missing
    # Assuming group might be part of the org_unit path if department is not set
    final_group = department
    if not final_group and org_unit:
        # Example: "/Students/KN-21" -> we can try to extract "KN-21"
        parts = org_unit.strip("/").split("/")
        if len(parts) > 1:
            final_group = parts[-1] 

    # Check if user exists
    user = session.exec(select(User).where(User.email == email)).first()
    
    if not user:
        # Auto-create new student
        user = User(
            email=email,
            full_name=final_name,
            group_name=final_group or "Невідомо",
            role=UserRole.STUDENT,
            hashed_password=None # Google users don't need a local password
        )
        session.add(user)
        print(f"Created new student user: {email} with group {user.group_name}")
    else:
        # Update name and group if changed in Google
        user.full_name = final_name
        if final_group and user.group_name != final_group:
            user.group_name = final_group
            print(f"Updated data for {email}: {final_name}, {final_group}")
        session.add(user)

    session.commit()
    session.refresh(user)

    # Issue JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": str(user.role.value if hasattr(user.role, 'value') else user.role)}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "role": str(user.role.value if hasattr(user.role, 'value') else user.role),
            "group_name": user.group_name
        }
    }
