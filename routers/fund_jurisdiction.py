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
from models import Investor_Manager,Fund_jurisdiction

class Fund_jursidiction_Request(BaseModel):
    fund_id: int=Field(gt=0)
    jurisdiction:str=Field(min_length=3)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency injection for the database session
db_dependency = Annotated[Session, Depends(get_db)]

router=APIRouter(
    prefix='/fund_jurisdiction',
    tags=['fund_jurisdiction']
)

@router.get("/",status_code=status.HTTP_200_OK)
async def get_all_jurisdictions(db:db_dependency):
    return db.query(Fund_jurisdiction).all()

@router.post("/add_jur/",status_code=status.HTTP_201_CREATED)
async def create_jurisdiction(db:db_dependency,jurisdiction:Fund_jursidiction_Request):
    try:
        fund_jur=Fund_jurisdiction(**jurisdiction.model_dump())
        db.add(fund_jur)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("specific/{jurisdiction_id}",status_code=status.HTTP_200_OK)
async def specific_jurisdictions(db:db_dependency,jurisdiction_id:int=Path(gt=0)):
    return db.query(Fund_jurisdiction).filter(Fund_jurisdiction.id==jurisdiction_id).first()

@router.get('all_jurisdictions',status_code=status.HTTP_200_OK)
async def all_jurisdiction_details(db:db_dependency):
    try:
        query = text("""
            SELECT imd.id as company_id, fj.*, fi.fund_name, imd.Company_name
            FROM fund_jurisdiction AS fj
            INNER JOIN fund_information AS fi ON fj.Fund_id = fi.id
            INNER JOIN invester_manager AS imd ON fi.company_id = imd.id;
        """)
        result = db.execute(query)
        rows = result.fetchall()

        # Convert the result into a list of dictionaries
        investors = [dict(row._mapping) for row in rows]
        return investors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/update/{jurisdiction_id}", status_code=status.HTTP_200_OK)
async def update_jurisdiction(db: db_dependency, jurisdiction: Fund_jursidiction_Request, jurisdiction_id: int):
    existing_jurisdiction = db.query(Fund_jurisdiction).filter(Fund_jurisdiction.id == jurisdiction_id).first()
    if not existing_jurisdiction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jurisdiction not found")
    
    existing_jurisdiction.fund_id = jurisdiction.fund_id
    existing_jurisdiction.jurisdiction = jurisdiction.jurisdiction
    
    try:
        db.commit()
        return existing_jurisdiction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
@router.delete("/delete/{del_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_jurisdiction(db:db_dependency,del_id:int=Path(gt=0)):
    jur=db.query(Fund_jurisdiction).filter(Fund_jurisdiction.id==del_id).first()
    if jur is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jurisdiction not found")
    db.query(Fund_jurisdiction).filter(Fund_jurisdiction.id==del_id).delete()
    db.commit()