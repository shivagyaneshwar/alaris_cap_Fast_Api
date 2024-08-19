import random
import string
from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,Text,DECIMAL,event,DateTime,func,Boolean
from sqlalchemy.orm import relationship, backref

class Investor_Manager(Base):
    __tablename__="invester_manager"
    id =Column(Integer,primary_key=True,index=True)
    company_name=Column(String,nullable=False,unique=True)
    overview = Column(Text, nullable=True)
    contact_person = Column(String(50), nullable=True)
    contact_position = Column(String(50), nullable=True)
    contact_email = Column(String(50), nullable=True)
    website = Column(String(100), unique=True, nullable=True)
    phone_number = Column(String(15), nullable=True)
    
    # funds_relationship = relationship("FundInformation", backref="manager")
    
class FundInformation(Base):
    __tablename__ = "fund_information"

    id = Column(Integer, primary_key=True,index=True)
    company_id = Column(Integer, ForeignKey("invester_manager.id"), nullable=False)
    fund_name = Column(String(100), nullable=False)
    fund_information = Column(Text, nullable=True)
    isin = Column(String(50), unique=True, nullable=True)
    isin_generated = Column(String(50), unique=True, nullable=True)
    # company = relationship("invester_manager")
    # investor_manager = relationship("Investor_Manager", backref="funds")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.isin_generated = self.generate_isin_generated()

    def generate_isin_generated(self):
        if self.fund_name:
            prefix = self.fund_name[:2].upper()
            suffix = ''.join(random.choices(string.digits, k=6))
            return prefix + suffix
        return None

def generate_isin_generated(mapper, connection, target):
        target.isin_generated = target.generate_isin_generated()
    
event.listen(FundInformation, 'before_update', generate_isin_generated)

class Regulator(Base):
    __tablename__='Regulators'
    id = Column(Integer, primary_key=True,index=True)
    company_id = Column(Integer, ForeignKey('invester_manager.id'), nullable=False)
    regulator_name = Column(String(100), nullable=False)
    
class Fund_jurisdiction(Base):
    __tablename__='Fund_jurisdiction'
    id = Column(Integer, primary_key=True,index=True)
    fund_id = Column(Integer, ForeignKey('fund_information.id'), nullable=False)
    jurisdiction=Column(String(100), nullable=False)
    
class Service_provider(Base):
    __tablename__='Service_provider'
    id = Column(Integer, primary_key=True,index=True)
    Fund_id = Column(Integer, ForeignKey('fund_information.id'), nullable=False)
    Prime_Brokers = Column(String(50), nullable=True)
    Custody = Column(String(50), nullable=True)
    Legal = Column(String(50), nullable=True)
    Audit = Column(String(50), nullable=True)
    Admin = Column(String(50), nullable=True)
    Trading_venues = Column(String(50), nullable=True)
    
class Share_class(Base):
    __tablename__='share_class'
    id = Column(Integer, primary_key=True,index=True)
    Fund_id = Column(Integer, ForeignKey('fund_information.id'), nullable=False)
    share_class_name = Column(String(100), nullable=False)
    investable = Column(String(50), nullable=False)
    Investment_style = Column(String(100), nullable=False)
    declared_investment_style = Column(String(100), nullable=False)
    Management_fee = Column(DECIMAL(10, 2), nullable=True)
    Performance_fee = Column(DECIMAL(10, 2), nullable=True)
    High_watermark = Column(String(100), nullable=True)
    Net_of_fees = Column(String(10), nullable=False)
    Lock_up_period_in_months = Column(Integer, nullable=True)
    subscription_currency = Column(String(50), nullable=True)
    Min_subscription = Column(Integer, nullable=True)
    Redemption_frequency = Column(String(100), nullable=True)
    Redemption_notice_in_months = Column(Integer, nullable=True)
    subscription_frequency = Column(Integer, nullable=True)
    Subsequent_subscription = Column(Integer, nullable=True)
    AUM = Column(Integer, nullable=True)
    
class Performance_returns(Base):
    __tablename__='performance_returns'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    share_class_id = Column(Integer, ForeignKey('share_class.id'), nullable=False)
    Year = Column(Integer, nullable=False)
    Jan = Column(DECIMAL(10, 4), nullable=True, default=None)
    Feb = Column(DECIMAL(10, 4), nullable=True, default=None)
    Mar = Column(DECIMAL(10, 4), nullable=True, default=None)
    Apr = Column(DECIMAL(10, 4), nullable=True, default=None)
    May = Column(DECIMAL(10, 4), nullable=True, default=None)
    Jun = Column(DECIMAL(10, 4), nullable=True, default=None)
    Jul = Column(DECIMAL(10, 4), nullable=True, default=None)
    Aug = Column(DECIMAL(10, 4), nullable=True, default=None)
    Sep = Column(DECIMAL(10, 4), nullable=True, default=None)
    Oct = Column(DECIMAL(10, 4), nullable=True, default=None)
    Nov = Column(DECIMAL(10, 4), nullable=True, default=None)
    Dec = Column(DECIMAL(10, 4), nullable=True, default=None)
    Yearly_returns = Column(DECIMAL(10, 4), nullable=True, default=0)
    Cumulative_returns = Column(DECIMAL(15, 12), nullable=True, default=None)
    Returns = Column(DECIMAL(10, 2), nullable=True, default=None)
    
def calculate_returns(mapper, connection, target):
    monthly_returns = [
        target.Jan, target.Feb, target.Mar, target.Apr,
        target.May, target.Jun, target.Jul, target.Aug,
        target.Sep, target.Oct, target.Nov, target.Dec
    ]
    
    target.Yearly_returns = sum(filter(None, monthly_returns))  # Sum of non-None values
    
    cumulative_return = 1
    for monthly_return in monthly_returns:
        if monthly_return is not None:
            cumulative_return *= (1 + monthly_return)
    target.Cumulative_returns = cumulative_return - 1

event.listen(Performance_returns, 'before_insert', calculate_returns)
event.listen(Performance_returns, 'before_update', calculate_returns)

class Role(Base):
    __tablename__ = 'Roles'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    
    # Relationship to User
    users = relationship('Users', back_populates='role')
    
    permissions = relationship('Permissions', back_populates='role')

class Users(Base):
    __tablename__ = 'Users'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(50), nullable=False, unique=True)
    password_hash = Column(Text)
    role_id = Column(Integer, ForeignKey('Roles.id'), nullable=False)  # Foreign key to Roles.id
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    google_sub = Column(String(255),nullable=True)
    
    # Relationship to Role
    role = relationship('Role', back_populates='users')
    
    
    
class Permissions(Base):
    __tablename__ = 'Permissions'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('Roles.id'), nullable=False)  # Foreign key to Roles.id
    table_name = Column(String(50), nullable=False)  # Name of the table
    create = Column(Boolean, default=False, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    update = Column(Boolean, default=False, nullable=False)
    delete = Column(Boolean, default=False, nullable=False)
    
    # Relationship to Role
    role = relationship('Role', back_populates='permissions')