import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Set up paths
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from agents import EmergencyOrchestrator
from backend.models import create_database, get_session, EmergencyCall, ConversationTurn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize FastAPI app
app = FastAPI(
    title="Emergency Response System API",
    description="Multi-agent emergency response assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
orchestrator: EmergencyOrchestrator = None
db_engine = None

# Pydantic models for API
class StartSessionRequest(BaseModel):
    caller_info: Optional[Dict[str, Any]] = None

class MessageRequest(BaseModel):
    session_id: str
    message: str

class MessageResponse(BaseModel):
    message: str
    agent_type: str
    confidence: float
    urgency_level: str
    session_id: str
    metadata: Dict[str, Any]

class SessionStatus(BaseModel):
    session_id: str
    start_time: str
    duration: str
    turn_number: int
    urgency_level: str
    emergency_type: str
    triage_complete: bool
    dispatch_attempted: bool
    dispatch_successful: bool
    empathy_score: float
    avg_response_time: float

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global orchestrator, db_engine
    
    # Load configuration
    app_config = config['development']
    
    # Initialize database
    db_engine = create_database(app_config.DATABASE_URL)
    
    # Initialize orchestrator
    orchestrator = EmergencyOrchestrator(app_config.__dict__)
    
    logging.info("Emergency Response System API started successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Emergency Response System API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/sessions/start")
async def start_session(request: StartSessionRequest) -> Dict[str, str]:
    """Start a new emergency session"""
    try:
        session_id = await orchestrator.start_session(request.caller_info)
        
        # Log to database
        await log_session_start(session_id, request.caller_info)
        
        return {
            "session_id": session_id,
            "status": "started",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logging.error(f"Error starting session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/message")
async def send_message(
    session_id: str, 
    request: MessageRequest,
    background_tasks: BackgroundTasks
) -> MessageResponse:
    """Send a message to the emergency response system"""
    try:
        if request.session_id != session_id:
            raise HTTPException(status_code=400, detail="Session ID mismatch")
        
        # Process message through orchestrator
        response = await orchestrator.process_message(session_id, request.message)
        
        # Add session_id to response
        response["session_id"] = session_id
        
        # Log conversation turn in background
        background_tasks.add_task(
            log_conversation_turn,
            session_id,
            request.message,
            response
        )
        
        return MessageResponse(**response)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}/status")
async def get_session_status(session_id: str) -> SessionStatus:
    """Get current status of an emergency session"""
    try:
        status = orchestrator.get_session_status(session_id)
        return SessionStatus(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error getting session status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/end")
async def end_session(session_id: str) -> Dict[str, Any]:
    """End an emergency session"""
    try:
        summary = orchestrator.end_session(session_id)
        
        # Update database
        await log_session_end(session_id, summary)
        
        return {
            "summary": summary,
            "status": "ended",
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/active")
async def get_active_sessions() -> List[str]:
    """Get list of active session IDs"""
    try:
        return list(orchestrator.active_sessions.keys())
    except Exception as e:
        logging.error(f"Error getting active sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Detailed health check"""
    try:
        return {
            "status": "healthy",
            "active_sessions": len(orchestrator.active_sessions),
            "database": "connected" if db_engine else "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Database logging functions
async def log_session_start(session_id: str, caller_info: Optional[Dict[str, Any]]):
    """Log session start to database"""
    try:
        if db_engine:
            session = get_session(db_engine)
            
            emergency_call = EmergencyCall(
                session_id=session_id,
                caller_phone=caller_info.get("phone") if caller_info else None,
                latitude=caller_info.get("latitude") if caller_info else None,
                longitude=caller_info.get("longitude") if caller_info else None,
                address=caller_info.get("address") if caller_info else None
            )
            
            session.add(emergency_call)
            session.commit()
            session.close()
    except Exception as e:
        logging.error(f"Error logging session start: {str(e)}")

async def log_conversation_turn(session_id: str, user_message: str, agent_response: Dict[str, Any]):
    """Log conversation turn to database"""
    try:
        if db_engine:
            db_session = get_session(db_engine)
            
            # Get call record
            call = db_session.query(EmergencyCall).filter_by(session_id=session_id).first()
            if call:
                turn = ConversationTurn(
                    call_id=call.id,
                    turn_number=len(call.conversation_turns) + 1,
                    user_message=user_message,
                    agent_response=agent_response.get("message", ""),
                    agent_type=agent_response.get("agent_type", "unknown"),
                    confidence_score=agent_response.get("confidence", 0.0),
                    sentiment_score=agent_response.get("metadata", {}).get("sentiment_score")
                )
                
                db_session.add(turn)
                db_session.commit()
            
            db_session.close()
    except Exception as e:
        logging.error(f"Error logging conversation turn: {str(e)}")

async def log_session_end(session_id: str, summary: Dict[str, Any]):
    """Log session end to database"""
    try:
        if db_engine:
            db_session = get_session(db_engine)
            
            call = db_session.query(EmergencyCall).filter_by(session_id=session_id).first()
            if call:
                call.end_time = datetime.utcnow()
                call.urgency_level = summary.get("urgency_level", "unknown")
                call.emergency_type = summary.get("emergency_type", "unknown")
                call.empathy_score = summary.get("empathy_score", 0.0)
                call.resolution_status = "completed"
                
                db_session.commit()
            
            db_session.close()
    except Exception as e:
        logging.error(f"Error logging session end: {str(e)}")

# Mock dispatch endpoint for testing
@app.post("/dispatch")
async def mock_dispatch_endpoint(dispatch_data: Dict[str, Any]):
    """Mock 911 dispatch endpoint for testing"""
    logging.info(f"Mock dispatch received: {dispatch_data}")
    
    return {
        "success": True,
        "reference_id": f"MOCK-{datetime.now().strftime('%Y%m%d')}-{hash(str(dispatch_data)) % 10000:04d}",
        "service": dispatch_data.get("service_needed", "EMS"),
        "priority": dispatch_data.get("priority", "Priority 3"),
        "estimated_arrival": "8-12 minutes"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
