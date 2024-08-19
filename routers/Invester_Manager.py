from fastapi import Depends, FastAPI, HTTPException,APIRouter,Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List,Optional
from database import engine, SessionLocal
from starlette import status
import models
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from models import Investor_Manager,FundInformation
from .services import user_dependency

router=APIRouter(
    prefix='/investment_manager',
    tags=['investor']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

class Investor_ManagerRequest(BaseModel):
    company_name: str = Field(max_length=50)
    overview: Optional[str] =None
    contact_person: str = Field(max_length=50)
    contact_position: str = Field(max_length=50)
    contact_email: str = Field(max_length=100)
    website: str
    phone_number: str = Field(max_length=12)
    
@router.get("/raw_sql",status_code=status.HTTP_200_OK)
async def read_all_raw_sql(db: db_dependency):
    try:
        result = db.execute(text("SELECT * FROM invester_manager"))
        # result=db.query(Investor_Manager).all()
        rows = result.fetchall()
        # Convert the result into a list of dictionaries
        investors = [dict(row._mapping) for row in rows]
        return investors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/add_invester_manager",status_code=status.HTTP_201_CREATED)
async def add_investor(investor:Investor_ManagerRequest,db:db_dependency):
    invest=Investor_Manager(**investor.model_dump())
    db.add(invest)
    db.commit()
    
@router.get("/raw_sql/{ivm_id}",status_code=status.HTTP_200_OK)
async def read_specific(db: db_dependency,ivm_id:int):
    try:
        query = text("SELECT * FROM invester_manager WHERE id = :ivm_id")
        result = db.execute(query, {'ivm_id': ivm_id})
        rows = result.fetchall()
        # Convert the result into a list of dictionaries
        investors = [dict(row._mapping) for row in rows]
        return investors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/update_invester_manager/{ivm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_investor(ivm_id: int, investor: Investor_ManagerRequest, db: db_dependency):
    invest = db.query(Investor_Manager).filter(Investor_Manager.id == ivm_id).first()
    if invest is None:
        raise HTTPException(status_code=404, detail="Investor Manager not found")

    # Update the fields explicitly
    invest.company_name = investor.company_name
    invest.overview = investor.overview
    invest.contact_person = investor.contact_person
    invest.contact_position = investor.contact_position
    invest.contact_email = investor.contact_email
    invest.website = investor.website
    invest.phone_number = investor.phone_number

    db.commit()
    db.refresh(invest)
    return invest

@router.delete("/delete_ivm/{ivm_id}", status_code=status.HTTP_204_NO_CONTENT)
async  def delete_ivm(db:db_dependency,ivm_id:int=Path(gt=0)):
    ivm=db.query(Investor_Manager).filter(Investor_Manager.id==ivm_id).first()
    if ivm is None:
        raise HTTPException(status_code=404,detail="doesnt exist")
    db.query(Investor_Manager).filter(Investor_Manager.id==ivm_id).delete()
    db.commit()

