from fastapi import Depends, FastAPI, HTTPException,APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List,Optional  # noqa: F401
from database import SessionLocal
from starlette import status
import models
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from models import Investor_Manager,Regulator


        
router=APIRouter(
    prefix='/Regulator',
    tags=['regulators']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency=Annotated[Session,Depends(get_db)]

class Regulator_request(BaseModel):
    company_id: int
    regulator_name:str=Field(min_length=3)
    
@router.get("/",status_code=status.HTTP_200_OK)
async def get_all_regulators(db:db_dependency):
    return db.query(Regulator).all()

@router.post("/add/",status_code=status.HTTP_201_CREATED)
async def add_regulator(db:db_dependency,regulator:Regulator_request):
    new_regulator=Regulator(**regulator.model_dump())
    db.add(new_regulator)
    db.commit()
    
@router.get("/{regulator_id}",status_code=status.HTTP_200_OK)
async def regulator_by_id(db:db_dependency,regulator_id:int):
    return db.query(Regulator).filter(Regulator.id==regulator_id).first()

@router.get("/query_regulators")
async def query_regulators(db:db_dependency):
    try:
        query = select(Regulator, Investor_Manager.id).join(Investor_Manager)
        results = db.execute(query).fetchall()
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/all_regulators/")
def get_fund_information_with_manager_details(db:db_dependency):
    query = """
        SELECT regulators.*, invester_manager.company_name
FROM Regulators AS regulators
INNER JOIN invester_manager ON regulators.company_id = invester_manager.id
    """
    result = db.execute(text(query))
    fund_info_with_manager_details = result.fetchall()
    fund_information_table = [dict(row._mapping) for row in fund_info_with_manager_details]
    return fund_information_table

@router.delete("/del_regulator/{del_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_regulator(db:db_dependency,del_id:int):
    
    todo_model=db.query(Regulator).filter(Regulator.id==del_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="doesnt exist")
    db.query(Regulator).filter(Regulator.id==del_id).delete()
    db.commit()
    
@router.put("/update/{regulator_id}", status_code=status.HTTP_200_OK)
async def update_regulator( regulator_data: Regulator_request, db: db_dependency,regulator_id: int):
    # Fetch the existing regulator
    existing_regulator = db.query(Regulator).filter(Regulator.id == regulator_id).first()
    if not existing_regulator:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Regulator with id {regulator_id} not found")
    
    # Update the fields
    existing_regulator.company_id = regulator_data.company_id
    existing_regulator.regulator_name = regulator_data.regulator_name

    # Commit the changes to the database
    db.commit()

