from fastapi import Depends, HTTPException, APIRouter, Path
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import SessionLocal
from starlette import status

# import models
from typing import Annotated
from models import Service_provider


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/Service_providers", tags=["service_provider"])


class ServiceProviderCreate(BaseModel):
    Fund_id: int
    Prime_Brokers: Optional[str] = None
    Custody: Optional[str] = None
    Legal: Optional[str] = None
    Audit: Optional[str] = None
    Admin: Optional[str] = None
    Trading_venues: Optional[str] = None


@router.get("/")
async def read_all(db: db_dependency):
    return db.query(Service_provider).all()


@router.post("/add_service", status_code=status.HTTP_201_CREATED)
async def create_service_provider(
    db: db_dependency, service_provider: ServiceProviderCreate
):
    new_sp = Service_provider(**service_provider.model_dump())
    db.add(new_sp)
    db.commit()


@router.get("/s_p/{sp_id}", status_code=status.HTTP_200_OK)
async def read_service_provider(db: db_dependency, sp_id: int = Path(gt=0)):
    service_provider = (
        db.query(Service_provider).filter(Service_provider.id == sp_id).first()
    )
    if service_provider is not None:
        return service_provider
    raise HTTPException(status_code=404, detail="not found")


@router.put("/update_sp/{sp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_sp(
    service: ServiceProviderCreate, db: db_dependency, sp_id: int = Path(gt=0)
):
    service_provider = (
        db.query(Service_provider).filter(Service_provider.id == sp_id).first()
    )
    if service_provider is None:
        raise HTTPException(status_code=404, detail="ServiceProvider doesn't exist")

    service_provider.Admin = service.Admin
    service_provider.Audit = service.Audit
    service_provider.Prime_Brokers = service.Prime_Brokers
    service_provider.Custody = service.Custody
    service_provider.Legal = service.Legal
    service_provider.Trading_venues = service.Trading_venues

    db.commit()
    db.refresh(service_provider)
    return service_provider

@router.delete('del_sp/{sp_id}',status_code=status.HTTP_204_NO_CONTENT)
async def delete_sp(db:db_dependency,sp_id:int):
    service_provider = (
        db.query(Service_provider).filter(Service_provider.id == sp_id).first()
    )
    if service_provider is None:
        raise HTTPException(status_code=404,detail="doesnt exist")
    db.query(Service_provider).filter(Service_provider.id==sp_id).delete()
    db.commit()
    
@router.get("/db_query/")
def get_fund_information_with_manager_details(db:db_dependency):
    query = """
        SELECT imd.id as company_id,fi.id as fund_id,sp.id,imd.Company_Name,fi.fund_name, sp.*
    FROM service_provider sp
    INNER JOIN fund_information fi
    ON sp.fund_id = fi.id
    INNER JOIN invester_manager imd on fi.company_id = imd.id
    """
    result = db.execute(text(query))
    fund_info_with_manager_details = result.fetchall()
    fund_information_table = [dict(row._mapping) for row in fund_info_with_manager_details]
    return fund_information_table