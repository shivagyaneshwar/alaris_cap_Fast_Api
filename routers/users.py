from fastapi import Depends, FastAPI, HTTPException, APIRouter, Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from database import engine, SessionLocal
from starlette import status
import models
from typing import Annotated
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from models import Investor_Manager, FundInformation, Users,Role
from routers import Invester_Manager
import bcrypt  # Import the bcrypt library

router = APIRouter(
    prefix='/users',
    tags=['user_detail']
)

class UserModel(BaseModel):
    username: str = Field(max_length=20)
    email: str = Field(min_length=5, max_length=100)
    password_hash: str
    role_id: Optional[int] = None
    
class PermissionResponse(BaseModel):
    id: int
    role_id: int
    table_name: str
    create: bool
    read: bool
    update: bool
    delete: bool

    class Config:
        from_attributes = True
        

class RoleResponse(BaseModel):
    id: int
    role_name: str
    permissions: List[PermissionResponse] = []  # Include permissions

    class Config:
        from_attributes = True 
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Optional[RoleResponse] = None  # Include role information

    class Config:
        from_attributes = True 
        


    # @validator('role')
    # def check_role(cls, value):
    #     if value not in {'admin', 'viewer', 'editor'}:
    #         raise ValueError('Role must be either admin, viewer, or editor')
    #     return value

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency injection for the database session
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
async def get_all_users(db: db_dependency):
    # Fetch all users with their associated roles and permissions
    users = db.query(Users).options(
        joinedload(Users.role).joinedload(Role.permissions)
    ).all()

    return users

@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def new_user(userM: UserModel, db: db_dependency):
    # Hash the password
    hashed_password = bcrypt.hashpw(userM.password_hash.encode('utf-8'), bcrypt.gensalt())
    user_data = userM.dict()
    user_data['password_hash'] = hashed_password.decode('utf-8')

    # Check if role_id is provided
    if 'role_id' in user_data and user_data['role_id'] is not None:
        role = db.query(Role).filter_by(id=user_data['role_id']).first()
        if role is None:
            raise HTTPException(status_code=400, detail="Role not found")
        user_data['role'] = role  # Ensure this is an instance of Role, not just the ID

    # Create a new user instance
    user = Users(
        username=user_data['username'],
        email=user_data['email'],
        password_hash=user_data['password_hash'],
        role=user_data.get('role')  # This should be an instance of Role or None
    )

    # Add the user to the database session
    db.add(user)
    db.commit()
    db.refresh(user)  # Refresh to get the ID and other fields if needed

    return user

# @router.post("/sign_up", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# async def new_user(userM: UserModel, db: Session = Depends(get_db)):
#     # Hash the password before storing it
#     hashed_password = bcrypt.hashpw(userM.password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

#     # Check if the role_id is provided and valid
#     role = None
#     if userM.role_id:
#         role = db.query(Role).filter_by(id=userM.role_id).first()
#         if role is None:
#             raise HTTPException(status_code=400, detail="Role not found")

#     # Create a new user instance with explicit attributes
#     user = Users(
#         username=userM.username,
#         email=userM.email,
#         password_hash=hashed_password,
#         role=role  # Assumes `role` is a valid Role object or None
#     )

#     # Add the user to the database sessio
#     db.add(user)
#     db.commit()
       