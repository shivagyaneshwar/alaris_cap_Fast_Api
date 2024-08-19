from fastapi import Depends, FastAPI, HTTPException, APIRouter, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from database import engine, SessionLocal
from starlette import status
import models
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from models import Investor_Manager, FundInformation, Users,Role
from routers import Invester_Manager
import bcrypt  # Import the bcrypt library

router = APIRouter(
    prefix='/roles',
    tags=['Roles_creation']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency injection for the database session
db_dependency = Annotated[Session, Depends(get_db)]

class Role_request(BaseModel):
    role_name:str=Field(min_length=5, max_length=100)
    
@router.get("/roles",status_code=status.HTTP_200_OK)
async def get_all_roles(db:db_dependency):
    return db.query(Role).all()

@router.post("add_role",status_code=status.HTTP_201_CREATED)
async def add_role(db:db_dependency,role:Role_request):
    role_created=Role(**role.model_dump())
    db.add(role_created)
    db.commit()