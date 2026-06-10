"""
Database models for ResQAlert system
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config.settings import settings

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WeatherData(Base):
    """Store weather data from APIs"""
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    pressure = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
class DisasterPrediction(Base):
    """Store disaster predictions"""
    __tablename__ = "disaster_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    disaster_type = Column(String(50), nullable=False)  # flood, drought, heatwave
    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_level = Column(String(20), nullable=False)  # low, medium, high
    prediction_date = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime)
    
class SafeZone(Base):
    """Store safe zone locations"""
    __tablename__ = "safe_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    location_type = Column(String(50))  # hospital, school, community_center
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer)
    contact_number = Column(String(20))
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    
class User(Base):
    """Store user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(100))
    alert_preferences = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Alert(Base):
    """Store sent alerts"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    disaster_type = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    alert_type = Column(String(20))  # sms, email
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="sent")  # sent, delivered, failed
    
    user = relationship("User", back_populates="alerts")

User.alerts = relationship("Alert", back_populates="user")

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
