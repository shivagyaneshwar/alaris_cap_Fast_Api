from fastapi import Depends, FastAPI, HTTPException,APIRouter
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field,validator
from typing import List,Optional
from database import engine, SessionLocal
from starlette import status
import models
from typing import Annotated
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from models import Investor_Manager,FundInformation,Share_class
from routers import Invester_Manager

router = APIRouter(
    prefix='/share_class',
    tags=['share_class']
)

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]

class ShareClassCreate(BaseModel):
    Fund_id: int
    share_class_name: str
    investable: str
    Investment_style: str
    declared_investment_style: str=Field(example=["Market Neutral", "Fundamental", "Long Short"])
    Management_fee: Optional[float] = None
    Performance_fee: Optional[float] = None
    High_watermark: Optional[str] = None
    Net_of_fees: str
    Lock_up_period_in_months: Optional[int] = None
    subscription_currency: Optional[str] = None
    Min_subscription: Optional[int] = None
    Redemption_frequency: Optional[int] = None
    Redemption_notice_in_months: Optional[int] = None
    subscription_frequency: Optional[str] = None
    Subsequent_subscription: Optional[int] = None
    AUM: Optional[int] = None
    
    @validator('declared_investment_style')
    def validate_declared_investment_style(cls, v):
        valid_styles = ["Fundamental", "Market Neutral", "Long Short"]
        if v not in valid_styles:
            raise ValueError(f"Invalid declared investment style: {v}. Must be one of: {', '.join(valid_styles)}")
        return v
    @validator('Investment_style')
    def validate_investment_style(cls, v):
        valid_styles = ["Fundamental", "Market Neutral", "Long Short"]
        if v not in valid_styles:
            raise ValueError(f"Invalid declared investment style: {v}. Must be one of: {', '.join(valid_styles)}")
        return v
    
@router.post("/",status_code=status.HTTP_200_OK)
async def add_all_share_classes(db:db_dependency,share_class:ShareClassCreate):
    share_class_created=Share_class(**share_class.model_dump())
    db.add(share_class_created)
    db.commit()
    return share_class

@router.get("/share",status_code=status.HTTP_200_OK)
async def get_all_share_classes(db:db_dependency):
    return db.query(Share_class).all()

@router.get("/all_details_share_class/")
async def get_fund_information_with_manager_details(db:db_dependency):
    query = """
        SELECT
    sc.id,
        fi.id as fund_id,
        im.id as manager_id,
        im.Company_name as company_name,
        fi.Fund_name as fund_name,
        sc.share_class_name,
        sc.investable,
        sc.Investment_style,
        sc.declared_investment_style,
        sc.Management_fee,
        sc.Performance_fee,
        sc.High_watermark,
        sc.Net_of_fees,
        sc.Lock_up_period_in_months,
        sc.subscription_currency,
        sc.Min_subscription,
        sc.Redemption_frequency,
        sc.Redemption_notice_in_months,
        sc.subscription_frequency,
        sc.Subsequent_subscription,
        sc.AUM
FROM
    share_class sc
INNER JOIN
    fund_information fi ON sc.Fund_id = fi.id
INNER JOIN
    invester_manager im ON fi.company_id = im.id
ORDER BY
    sc.id;

    """
    result = db.execute(text(query))
    fund_info_with_manager_details = result.fetchall()
    fund_information_table = [dict(row._mapping) for row in fund_info_with_manager_details]
    return fund_information_table

@router.put("/share-classes/{share_class_id}")
async def update_share_class( share_class_data: ShareClassCreate, db: db_dependency,share_class_id: int,):
    # Check if the share class with given ID exists
    share_class = db.query(Share_class).filter(Share_class.id == share_class_id).first()
    if not share_class:
        raise HTTPException(status_code=404, detail="Share class not found")
    
    # Update the share class object with new data
    update_data = {
        "Fund_id": share_class_data.Fund_id,
        "share_class_name": share_class_data.share_class_name,
        "investable": share_class_data.investable,
        "Investment_style": share_class_data.Investment_style,
        "declared_investment_style": share_class_data.declared_investment_style,
        "Management_fee": share_class_data.Management_fee,
        "Performance_fee": share_class_data.Performance_fee,
        "High_watermark": share_class_data.High_watermark,
        "Net_of_fees": share_class_data.Net_of_fees,
        "Lock_up_period_in_months": share_class_data.Lock_up_period_in_months,
        "subscription_currency": share_class_data.subscription_currency,
        "Min_subscription": share_class_data.Min_subscription,
        "Redemption_frequency": share_class_data.Redemption_frequency,
        "Redemption_notice_in_months": share_class_data.Redemption_notice_in_months,
        "subscription_frequency": share_class_data.subscription_frequency,
        "Subsequent_subscription": share_class_data.Subsequent_subscription,
        "AUM": share_class_data.AUM
    }

    # Update the share class in the database
    db.query(Share_class).filter(Share_class.id == share_class_id).update(update_data)
    db.commit()
    
    return {"message": "Share class updated successfully"}

@router.get("/share_class/{share_class_id}/details")
async def get_share_class_details(share_class_id: int, db: db_dependency):
    query = """
        SELECT
    sc.id AS id,
    fi.id AS fund_id,
    im.id AS manager_id,
    im.company_name,
    fi.fund_name,
    sc.share_class_name,
    sc.investable,
    sc.Investment_style,
    sc.declared_investment_style,
    sc.Management_fee,
    sc.Performance_fee,
    sc.High_watermark,
    sc.Net_of_fees,
    sc.Lock_up_period_in_months,
    sc.subscription_currency,
    sc.Min_subscription,
    sc.Redemption_frequency,
    sc.Redemption_notice_in_months,
    sc.subscription_frequency,
    sc.Subsequent_subscription,
    sc.AUM
FROM
    share_class sc
INNER JOIN
    fund_information fi ON sc.Fund_id = fi.id
INNER JOIN
    invester_manager im ON fi.company_id = im.id
WHERE
        sc.id = :share_class_id
ORDER BY
    sc.id
    """
    result = db.execute(text(query), {"share_class_id": share_class_id})
    share_class_details = result.fetchall()
    if not share_class_details:
        raise HTTPException(status_code=404, detail="Share class not found")
    fund_information_table = [dict(row._mapping) for row in share_class_details]
    return fund_information_table

@router.delete('/del/{del_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_share_class(db:db_dependency,del_id:int):
    share_class=db.query(Share_class).filter(Share_class.id==del_id).first()
    if share_class is None:
         raise HTTPException(status_code=404,detail="doesnt exist")
    db.query(Share_class).filter(Share_class.id==del_id).delete()
    db.commit()

@router.get('/company_id/{com_id}', status_code=status.HTTP_200_OK)
async def get_specific_fund_based(com_id: int, db: db_dependency):
    query = text("SELECT id, share_class_name FROM share_class WHERE fund_id = :com_id")
    result = db.execute(query, {'com_id': com_id})
    rows = result.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Fund information not found")
    
    # Convert the result into a list of dictionaries
    funds = [dict(row._mapping) for row in rows]
    return funds
