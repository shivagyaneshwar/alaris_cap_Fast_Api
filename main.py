import secrets
from fastapi import Depends, FastAPI,Request
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
from routers import permissions,auth,roles,Invester_Manager,fund_information,share_class,performance_returns,regulator,fund_jurisdiction,service_providers,users
from starlette.middleware.sessions import SessionMiddleware
import logging
# Ensure models are created
models.Base.metadata.create_all(bind=engine)

origins = ["*"]

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
# Pydantic model for request body
# class Investor_ManagerRequest(BaseModel):
#     company_name: str = Field(max_length=50)
#     overview: str
#     contact_person: str = Field(max_length=50)
#     contact_position: str = Field(max_length=50)
#     contact_email: str = Field(max_length=100)
#     website: str
#     phone_number: str = Field(max_length=12)
    
    
SECRET_KEY = "Nz2E5k1WfB9XG7p2fGq9Q5s8aW1lQ4i3o7sU9pQ5rV8bK6fZ"

app = FastAPI()

origins = [
    "http://localhost:3000",  # React app default port
    "http://127.0.0.1:3000",  # React app alternative localhost address
    # Add other origins as needed
]

app.add_middleware(SessionMiddleware, secret_key="Nz2E5k1WfB9XG7p2fGq9Q5s8aW1lQ4i3o7sU9pQ5rV8bK6fZ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

#https://www.tcs.com/careers/india/tcs-fresher-hiring-nqt-2024
app.include_router(permissions.router)
app.include_router(roles.router)
app.include_router(Invester_Manager.router)
app.include_router(fund_information.router)
app.include_router(share_class.router)
app.include_router(performance_returns.router)
app.include_router(regulator.router)
app.include_router(fund_jurisdiction.router)
app.include_router(service_providers.router)
app.include_router(users.router)
app.include_router(auth.router)


@app.get("/set-session")
async def set_session(request: Request):
    state = secrets.token_urlsafe(16)
    request.session['state'] = state
    logging.debug(f"Set session state: {state}")
    return {"state": state}

@app.get("/get-session")
async def get_session(request: Request):
    state = request.session.get('state')
    logging.debug(f"Retrieved session state: {state}")
    if state is None:
        return {"error": "Session state not found"}
    return {"state": state}
