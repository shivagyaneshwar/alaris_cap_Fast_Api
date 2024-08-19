from fastapi import Depends, FastAPI, HTTPException,APIRouter,Path
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field,condecimal
from typing import List,Optional
from database import engine, SessionLocal
from starlette import status
import models
from typing import Annotated,Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from models import Investor_Manager,FundInformation,Performance_returns
from routers import Invester_Manager

router=APIRouter(
    prefix='/performance_returns',
    tags=['performance_ret']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

class PerformanceReturnsBase(BaseModel):
    share_class_id: int
    Year: int
    Jan: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="January returns")
    Feb: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="February returns")
    Mar: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="March returns")
    Apr: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="April returns")
    May: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="May returns")
    Jun: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="June returns")
    Jul: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="July returns")
    Aug: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="August returns")
    Sep: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="September returns")
    Oct: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="October returns")
    Nov: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="November returns")
    Dec: Optional[condecimal(max_digits=10, decimal_places=4)] = Field(None, description="December returns")
    

@router.post("/performance_returns/")
def create_performance_return(perf_return: PerformanceReturnsBase, db: db_dependency):
    db_perf_return = Performance_returns(**perf_return.model_dump())
    db.add(db_perf_return)
    db.commit()
    db.refresh(db_perf_return)
    return db_perf_return

@router.get("/")
def all_performance_returns(db:db_dependency):
    return db.query(Performance_returns).all()

@router.get("/get_all_performances",status_code=status.HTTP_200_OK)
async def get_all_performances_through_query(db:db_dependency):
    query = """
         SELECT
        pr.id,
        imd.id as manager_id,
        fi.id as fund_id,
        pr.share_class_id,
        imd.Company_name,
        fi.Fund_name,
        sc.share_class_name,
        pr.year,pr.Jan,pr.Feb,pr.Mar,pr.Apr,pr.May,pr.Jun,pr.Jul,pr.Aug,pr.Sep,pr.Oct,pr.Nov,pr.Dec,pr.Yearly_returns,pr.Cumulative_returns
    FROM
        fund_information AS fi
    INNER JOIN
        invester_manager AS imd
    ON
        fi.company_id = imd.id
    INNER JOIN
        share_class AS sc
    ON
        sc.fund_id = fi.id
    INNER JOIN
        performance_returns AS pr
    ON
        pr.share_class_id = sc.id
    ORDER BY
        fi.id
    """
    result = db.execute(text(query))
    fund_info_with_manager_details = result.fetchall()
    fund_information_table = [dict(row._mapping) for row in fund_info_with_manager_details]
    return fund_information_table

@router.put("/performance_returns/{performance_id}")
def update_performance_return(
    performance_id: int, 
    perf_return_update: PerformanceReturnsBase,
    db: db_dependency
):
    db_perf_return = db.query(Performance_returns).filter(Performance_returns.id == performance_id).first()
    
    if db_perf_return:
        db_perf_return.share_class_id = perf_return_update.share_class_id
        db_perf_return.Year = perf_return_update.Year
        db_perf_return.Jan = perf_return_update.Jan
        db_perf_return.Feb = perf_return_update.Feb
        db_perf_return.Mar = perf_return_update.Mar
        db_perf_return.Apr = perf_return_update.Apr
        db_perf_return.May = perf_return_update.May
        db_perf_return.Jun = perf_return_update.Jun
        db_perf_return.Jul = perf_return_update.Jul
        db_perf_return.Aug = perf_return_update.Aug
        db_perf_return.Sep = perf_return_update.Sep
        db_perf_return.Oct = perf_return_update.Oct
        db_perf_return.Nov = perf_return_update.Nov
        db_perf_return.Dec = perf_return_update.Dec
        
        db.commit()
        db.refresh(db_perf_return)
        
        return db_perf_return
    
    raise HTTPException(status_code=404, detail=f"Performance return with id {performance_id} not found")

@router.delete('/delete/{del_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_pr(db:db_dependency,del_id:int=Path(gt=0)):
    pr=db.query(Performance_returns).filter(Performance_returns.id==del_id).first()
    if pr is None:
        raise HTTPException(status_code=404,detail="Not found")
    db.query(Performance_returns).filter(Performance_returns.id==del_id).delete()
    db.commit()