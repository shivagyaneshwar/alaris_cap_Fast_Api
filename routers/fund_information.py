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
from routers import Invester_Manager


router = APIRouter(
    prefix='/fund_information',
    tags=['fund_info']
)

class FundInformationRequest(BaseModel):
    company_id: int
    fund_name: str = Field(max_length=100)
    fund_information: str=None
    isin: str = Field(max_length=10)
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency injection for the database session
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    try:
        return db.query(FundInformation).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/add_fund_info",status_code=status.HTTP_201_CREATED)
async def add_fund_information(db:db_dependency,fund_request:FundInformationRequest):
    try:
        fund_info = FundInformation(**fund_request.model_dump())
        db.add(fund_info)
        db.commit()
        db.refresh(fund_info)
        return fund_info
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str('duplicate entry'))
    
@router.get("/fund_information_with_manager_details/")
async def get_fund_information_with_manager_details(db:db_dependency):
    query = """
        SELECT
            fund_information.id,
            fund_information.company_id,
            invester_manager.company_name,
            fund_information.fund_name,
            fund_information.fund_information,
            fund_information.isin,
            fund_information.isin_generated
        FROM
            fund_information
        INNER JOIN
            invester_manager
        ON
            fund_information.company_id = invester_manager.id
        ORDER BY
            fund_information.id
    """
    result = db.execute(text(query))
    fund_info_with_manager_details = result.fetchall()
    fund_information_table = [dict(row._mapping) for row in fund_info_with_manager_details]
    return fund_information_table
    

@router.put("/update_fund_info/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_fund_information(id: int, fund_request: FundInformationRequest, db: db_dependency):   
    fund_info = db.query(FundInformation).filter(FundInformation.id == id).first()
    if not fund_info:
        raise HTTPException(status_code=404, detail="Fund information not found")

    fund_info.company_id = fund_request.company_id
    fund_info.fund_name = fund_request.fund_name
    fund_info.fund_information = fund_request.fund_information
    fund_info.isin = fund_request.isin

    db.commit()
    db.refresh(fund_info)
    return fund_info

@router.delete('/delete/{del_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_fund_information(db:db_dependency,del_id:int=Path(gt=0)):
    fund_info=db.query(FundInformation).filter(FundInformation.id==del_id).first()
    if fund_info is None:
        raise HTTPException(status_code=404,detail="doesnt exist")
    db.query(FundInformation).filter(FundInformation.id==del_id).delete()
    db.commit()
    
@router.get('/specific_fund_info/{fund_id}',status_code=status.HTTP_200_OK)
async def get_specific_fund(db:db_dependency,fund_id:int):
    fund_info=db.query(FundInformation).filter(FundInformation.company_id==fund_id).all()
    if fund_info is None:
        raise HTTPException(status_code=404,detail="doesnt exist")
    return fund_info

@router.get('/company_id/{com_id}', status_code=status.HTTP_200_OK)
async def get_specific_fund_based(com_id: int, db: db_dependency):
    query = text("SELECT id, Fund_name FROM fund_information WHERE company_id = :com_id")
    result = db.execute(query, {'com_id': com_id})
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Fund information not found")
    
    # Convert the result into a list of dictionaries
    funds = [dict(row._mapping) for row in rows]
    return funds