from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class EmergencyCall(Base):
    __tablename__ = "emergency_calls"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    caller_phone = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    
    # Location data
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    
    # Triage information
    urgency_level = Column(String, default="unknown")  # critical, high, medium, low
    emergency_type = Column(String, nullable=True)  # medical, fire, police, other
    
    # Analytics
    empathy_score = Column(Float, default=0.0)
    triage_time = Column(Float, nullable=True)  # seconds
    resolution_status = Column(String, default="active")  # active, resolved, transferred
    
    # Metadata
    transcript = Column(Text, nullable=True)
    agent_responses = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConversationTurn(Base):
    __tablename__ = "conversation_turns"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, index=True)
    turn_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Message content
    user_message = Column(Text)
    agent_response = Column(Text)
    agent_type = Column(String)  # empathy, triage, guidance, dispatch
    
    # Analytics
    sentiment_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    response_time = Column(Float, nullable=True)  # seconds
    
    # Safety flags
    profanity_detected = Column(Boolean, default=False)
    safety_trigger = Column(Boolean, default=False)

class SystemMetrics(Base):
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Performance metrics
    avg_response_time = Column(Float)
    total_calls = Column(Integer)
    active_calls = Column(Integer)
    
    # Quality metrics
    avg_empathy_score = Column(Float)
    avg_triage_time = Column(Float)
    resolution_accuracy = Column(Float)
    
    # Safety metrics
    profanity_incidents = Column(Integer)
    safety_triggers = Column(Integer)

# Database setup
def create_database(database_url: str):
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    return engine

def get_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
