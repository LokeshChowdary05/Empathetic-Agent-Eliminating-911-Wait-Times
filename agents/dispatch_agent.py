import asyncio
import json
import requests
from typing import Dict, Any
from datetime import datetime
from .base_agent import BaseAgent, AgentResponse

class DispatchAgent(BaseAgent):
    """Agent responsible for dispatching emergency information to 911 services"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("DispatchAgent", config)
        self.dispatch_url = config.get("MOCK_DISPATCH_URL", "http://localhost:8001/dispatch")
        self.real_dispatch_enabled = config.get("REAL_DISPATCH_ENABLED", False)
        
        # Emergency service mapping
        self.service_mapping = {
            "medical": "EMS",
            "fire": "Fire Department",
            "police": "Police",
            "safety": "Police",
            "unknown": "EMS"  # Default to medical
        }
        
        # Priority mapping for dispatch
        self.priority_mapping = {
            "critical": "Priority 1",
            "high": "Priority 2", 
            "medium": "Priority 3",
            "low": "Priority 4",
            "unknown": "Priority 3"
        }
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process emergency information and dispatch to appropriate services"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Check if we have enough information to dispatch
            if not self._ready_to_dispatch(context):
                response_message = "Still gathering information before dispatch. Please continue providing details."
                
                response = AgentResponse(
                    message=response_message,
                    agent_type="dispatch",
                    confidence=0.3,
                    urgency_level=context.get("urgency_level", "unknown"),
                    metadata={
                        "dispatch_attempted": False,
                        "reason": "Insufficient information"
                    }
                )
                return response.to_dict()
            
            # Prepare dispatch information
            dispatch_data = self._prepare_dispatch_data(context)
            
            # Send to dispatch service
            dispatch_result = await self._send_to_dispatch(dispatch_data)
            
            response_time = asyncio.get_event_loop().time() - start_time
            
            if dispatch_result["success"]:
                response_message = f"Emergency services have been notified. {dispatch_result['service']} is being dispatched to your location. Reference number: {dispatch_result['reference_id']}"
            else:
                response_message = "There was an issue contacting emergency services. Please call 911 directly if possible."
            
            response = AgentResponse(
                message=response_message,
                agent_type="dispatch",
                confidence=0.95 if dispatch_result["success"] else 0.2,
                urgency_level=context.get("urgency_level", "unknown"),
                metadata={
                    "dispatch_attempted": True,
                    "dispatch_successful": dispatch_result["success"],
                    "reference_id": dispatch_result.get("reference_id"),
                    "service_type": dispatch_result.get("service"),
                    "response_time": response_time
                }
            )
            
            self.log_interaction(message, response_message, response_time, context)
            
            return response.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error in dispatch agent: {str(e)}")
            fallback_response = AgentResponse(
                message="Unable to automatically dispatch. Please call 911 directly.",
                agent_type="dispatch",
                confidence=0.1,
                metadata={"error": str(e)}
            )
            return fallback_response.to_dict()
    
    def _ready_to_dispatch(self, context: Dict[str, Any]) -> bool:
        """Check if we have minimum information needed for dispatch"""
        required_info = ["urgency_level", "emergency_type"]
        
        # Check for basic requirements
        has_basic_info = all(context.get(key) != "unknown" for key in required_info)
        
        # Check for location (critical for dispatch)
        has_location = (
            context.get("address") or 
            (context.get("latitude") and context.get("longitude")) or
            "location" in context.get("questions_asked", [])
        )
        
        # Check for sufficient triage information
        triage_complete = context.get("triage_complete", False)
        
        return has_basic_info and has_location and triage_complete
    
    def _prepare_dispatch_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare emergency data for dispatch"""
        urgency_level = context.get("urgency_level", "unknown")
        emergency_type = context.get("emergency_type", "unknown")
        
        dispatch_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "emergency_id": context.get("session_id", "unknown"),
            "caller_phone": context.get("caller_phone"),
            
            # Emergency details
            "emergency_type": emergency_type,
            "urgency_level": urgency_level,
            "priority": self.priority_mapping.get(urgency_level, "Priority 3"),
            "service_needed": self.service_mapping.get(emergency_type, "EMS"),
            
            # Location information
            "address": context.get("address"),
            "latitude": context.get("latitude"),
            "longitude": context.get("longitude"),
            
            # Incident details
            "description": context.get("incident_description", ""),
            "critical_keywords": context.get("critical_keywords", []),
            "victim_info": {
                "age": context.get("victim_age"),
                "conscious": context.get("victim_conscious"),
                "breathing": context.get("victim_breathing"),
                "medical_conditions": context.get("medical_conditions")
            },
            
            # Call metadata
            "call_duration": context.get("call_duration", 0),
            "empathy_score": context.get("empathy_score", 0),
            "triage_time": context.get("triage_time", 0),
            "transcript": context.get("transcript", "")
        }
        
        return dispatch_data
    
    async def _send_to_dispatch(self, dispatch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send emergency data to dispatch service"""
        try:
            if self.real_dispatch_enabled:
                # This would integrate with real 911 dispatch API
                # For now, we'll simulate success
                self.logger.warning("Real dispatch integration not implemented")
                return {
                    "success": False,
                    "reason": "Real dispatch not configured"
                }
            else:
                # Mock dispatch for development/demo
                return await self._mock_dispatch(dispatch_data)
                
        except Exception as e:
            self.logger.error(f"Dispatch failed: {str(e)}")
            return {
                "success": False,
                "reason": str(e)
            }
    
    async def _mock_dispatch(self, dispatch_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock dispatch service for development and demo"""
        try:
            # Simulate API call delay
            await asyncio.sleep(0.5)
            
            # Generate mock response
            service_type = dispatch_data.get("service_needed", "EMS")
            priority = dispatch_data.get("priority", "Priority 3")
            reference_id = f"EMG-{datetime.now().strftime('%Y%m%d')}-{hash(dispatch_data['emergency_id']) % 10000:04d}"
            
            # Log the dispatch (in real system, this would go to dispatch center)
            self.logger.info(f"MOCK DISPATCH: {service_type} {priority} - {reference_id}")
            self.logger.info(f"Location: {dispatch_data.get('address', 'Unknown')}")
            self.logger.info(f"Emergency: {dispatch_data.get('description', 'Unknown')}")
            
            return {
                "success": True,
                "service": service_type,
                "priority": priority,
                "reference_id": reference_id,
                "estimated_arrival": "8-12 minutes"
            }
            
        except Exception as e:
            return {
                "success": False,
                "reason": f"Mock dispatch error: {str(e)}"
            }
    
    def should_activate(self, context: Dict[str, Any]) -> bool:
        """Determine if dispatch agent should be activated"""
        # Activate when we have enough info to dispatch
        if self._ready_to_dispatch(context):
            return True
        
        # Activate for critical emergencies even with incomplete info
        urgency_level = context.get("urgency_level", "unknown")
        if urgency_level == "critical":
            return True
        
        return False
    
    def get_dispatch_status(self, session_id: str) -> Dict[str, Any]:
        """Get status of emergency dispatch"""
        # This would query the dispatch system for status
        # For now, return mock status
        return {
            "status": "dispatched",
            "estimated_arrival": "8-12 minutes",
            "units_en_route": ["Ambulance 42", "Fire Engine 7"]
        }
