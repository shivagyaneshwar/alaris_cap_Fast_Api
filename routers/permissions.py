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
from models import Investor_Manager, FundInformation, Users,Role,Permissions
from routers import Invester_Manager
import bcrypt  # Import the bcrypt library


        
router=APIRouter(
    prefix='/permissions',
    tags=['permissions']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency=Annotated[Session,Depends(get_db)]

@router.get("/permission",status_code=status.HTTP_200_OK)
async def all_roles_with_permissions(db:db_dependency):
    return db.query(Permissions).all()

class PermissionCreate(BaseModel):
    role_id: int
    table_name: str
    create: bool = Field(default=False)
    read: bool = Field(default=False)
    update: bool = Field(default=False)
    delete: bool = Field(default=False)
    
@router.post("/add_permission", status_code=status.HTTP_201_CREATED, response_model=PermissionCreate)
async def create_permission(permission: PermissionCreate, db: db_dependency):
    # Check if the role_id exists
    role = db.query(Role).filter(Role.id == permission.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    # Create the new permission
    db_permission = Permissions(
        role_id=permission.role_id,
        table_name=permission.table_name,
        create=permission.create,
        read=permission.read,
        update=permission.update,
        delete=permission.delete
    )
    
    # Add the permission to the database and commit
    db.add(db_permission)
    db.commit()
    
    # Refresh to get the updated data from the database
    db.refresh(db_permission)
    
    return db_permission

@router.get("/req_permission/",status_code=status.HTTP_200_OK)
async def get_roles_permissions(db:db_dependency,permission:int):
    role = db.query(Permissions).filter(Permissions.role_id == permission).all()
    return role

@router.put("/adjust_permission",status_code=status.HTTP_202_ACCEPTED)
async def modify_permissions(db:db_dependency,permission:PermissionCreate):
    permission_req=db.query(Permissions).filter(Permissions.role_id == permission.role_id).filter(Permissions.table_name==permission.table_name).first()
    if permission_req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    permission_req.create=permission.create
    permission_req.read=permission.read
    permission_req.delete=permission.delete
    permission_req.update=permission.update
    print(permission)
    db.commit()