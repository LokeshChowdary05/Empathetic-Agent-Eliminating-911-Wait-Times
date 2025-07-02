import asyncio
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .empathy_agent import EmpathyAgent
from .triage_agent import TriageAgent
from .guidance_agent import GuidanceAgent
from .dispatch_agent import DispatchAgent

class EmergencyOrchestrator:
    """Orchestrates multiple emergency response agents to provide comprehensive assistance"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("EmergencyOrchestrator")
        
        # Initialize agents
        self.empathy_agent = EmpathyAgent(config)
        self.triage_agent = TriageAgent(config)
        self.guidance_agent = GuidanceAgent(config)
        self.dispatch_agent = DispatchAgent(config)
        
        # Active sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Safety monitoring
        self.safety_keywords = config.get("SAFETY_KEYWORDS", [])
        self.max_conversation_turns = config.get("MAX_CONVERSATION_TURNS", 50)
        
    async def start_session(self, caller_info: Optional[Dict[str, Any]] = None) -> str:
        """Start a new emergency session"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "start_time": datetime.utcnow(),
            "caller_phone": caller_info.get("phone") if caller_info else None,
            "latitude": caller_info.get("latitude") if caller_info else None,
            "longitude": caller_info.get("longitude") if caller_info else None,
            "address": caller_info.get("address") if caller_info else None,
            
            # Conversation state
            "turn_number": 0,
            "conversation_history": [],
            "questions_asked": [],
            
            # Emergency assessment
            "urgency_level": "unknown",
            "emergency_type": "unknown",
            "critical_keywords": [],
            "triage_complete": False,
            "dispatch_attempted": False,
            "dispatch_successful": False,
            
            # Analytics
            "empathy_score": 0.0,
            "sentiment_scores": [],
            "response_times": [],
            "agent_activations": [],
            
            # Safety flags
            "safety_triggers": 0,
            "profanity_detected": False,
            "loop_breaker_active": False
        }
        
        self.active_sessions[session_id] = session_data
        self.logger.info(f"Started emergency session: {session_id}")
        
        return session_id
    
    async def process_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Process user message through appropriate agents"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Safety checks
            safety_check = self._perform_safety_checks(user_message, session)
            if safety_check["blocked"]:
                return safety_check
            
            # Update session state
            session["turn_number"] += 1
            session["conversation_history"].append({
                "turn": session["turn_number"],
                "user_message": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Determine which agents should be activated
            active_agents = self._determine_active_agents(user_message, session)
            
            # Process through agents
            agent_responses = await self._process_through_agents(
                user_message, session, active_agents
            )
            
            # Combine and prioritize responses
            final_response = self._combine_agent_responses(agent_responses, session)
            
            # Update session with response
            session["conversation_history"][-1]["agent_response"] = final_response["message"]
            session["conversation_history"][-1]["agent_type"] = final_response["agent_type"]
            
            # Update analytics
            processing_time = asyncio.get_event_loop().time() - start_time
            session["response_times"].append(processing_time)
            
            # Update session state from agent responses
            self._update_session_state(session, agent_responses)
            
            self.logger.info(f"Processed message for session {session_id} in {processing_time:.2f}s")
            
            return final_response
            
        except Exception as e:
            self.logger.error(f"Error processing message for session {session_id}: {str(e)}")
            return {
                "message": "I'm experiencing technical difficulties. Please call 911 directly if this is an emergency.",
                "agent_type": "system",
                "confidence": 0.1,
                "urgency_level": "unknown",
                "metadata": {"error": str(e)}
            }
    
    def _perform_safety_checks(self, message: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Perform safety checks on user message"""
        # Check for safety keywords
        message_lower = message.lower()
        safety_triggers = [keyword for keyword in self.safety_keywords 
                          if keyword.lower() in message_lower]
        
        if safety_triggers:
            session["safety_triggers"] += 1
            self.logger.warning(f"Safety trigger detected: {safety_triggers}")
            
            if "suicide" in safety_triggers or "self-harm" in safety_triggers:
                return {
                    "message": "I'm very concerned about what you've shared. Please call the National Suicide Prevention Lifeline at 988 or stay on the line while I connect you to emergency services immediately.",
                    "agent_type": "safety",
                    "confidence": 1.0,
                    "urgency_level": "critical",
                    "metadata": {
                        "blocked": True,
                        "safety_trigger": True,
                        "trigger_keywords": safety_triggers
                    }
                }
        
        # Check for conversation length
        if session["turn_number"] >= self.max_conversation_turns:
            session["loop_breaker_active"] = True
            return {
                "message": "We've been talking for a while. Let me connect you directly with emergency services to ensure you get immediate help.",
                "agent_type": "safety",
                "confidence": 1.0,
                "urgency_level": "high",
                "metadata": {
                    "blocked": True,
                    "loop_breaker": True
                }
            }
        
        return {"blocked": False}
    
    def _determine_active_agents(self, message: str, session: Dict[str, Any]) -> List[str]:
        """Determine which agents should be activated for this message"""
        active_agents = []
        
        # Context for agent decision making
        context = self._build_context(session, message)
        
        # Check each agent's activation criteria
        if self.empathy_agent.should_activate(context):
            active_agents.append("empathy")
        
        if self.triage_agent.should_activate(context):
            active_agents.append("triage")
        
        if self.guidance_agent.should_activate(context):
            active_agents.append("guidance")
        
        if self.dispatch_agent.should_activate(context):
            active_agents.append("dispatch")
        
        # Default activation rules
        if not active_agents:
            if session["turn_number"] == 1:
                active_agents = ["empathy", "triage"]
            else:
                active_agents = ["triage"]
        
        session["agent_activations"].append({
            "turn": session["turn_number"],
            "agents": active_agents
        })
        
        return active_agents
    
    async def _process_through_agents(self, message: str, session: Dict[str, Any], 
                                    active_agents: List[str]) -> Dict[str, Dict[str, Any]]:
        """Process message through all active agents"""
        context = self._build_context(session, message)
        agent_responses = {}
        
        # Process through agents concurrently
        tasks = []
        
        if "empathy" in active_agents:
            tasks.append(("empathy", self.empathy_agent.process_message(message, context)))
        
        if "triage" in active_agents:
            tasks.append(("triage", self.triage_agent.process_message(message, context)))
        
        if "guidance" in active_agents:
            tasks.append(("guidance", self.guidance_agent.process_message(message, context)))
        
        if "dispatch" in active_agents:
            tasks.append(("dispatch", self.dispatch_agent.process_message(message, context)))
        
        # Execute tasks
        for agent_name, task in tasks:
            try:
                response = await task
                agent_responses[agent_name] = response
            except Exception as e:
                self.logger.error(f"Error in {agent_name} agent: {str(e)}")
                agent_responses[agent_name] = {
                    "message": f"Error in {agent_name} processing",
                    "agent_type": agent_name,
                    "confidence": 0.1,
                    "metadata": {"error": str(e)}
                }
        
        return agent_responses
    
    def _build_context(self, session: Dict[str, Any], current_message: str) -> Dict[str, Any]:
        """Build context for agent processing"""
        return {
            "session_id": session["session_id"],
            "turn_number": session["turn_number"],
            "message": current_message,
            "conversation_history": session["conversation_history"],
            "questions_asked": session["questions_asked"],
            "urgency_level": session["urgency_level"],
            "emergency_type": session["emergency_type"],
            "critical_keywords": session["critical_keywords"],
            "triage_complete": session["triage_complete"],
            "empathy_score": session["empathy_score"],
            "address": session.get("address"),
            "latitude": session.get("latitude"),
            "longitude": session.get("longitude"),
            "caller_phone": session.get("caller_phone")
        }
    
    def _combine_agent_responses(self, agent_responses: Dict[str, Dict[str, Any]], 
                               session: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple agent responses into a single response"""
        if not agent_responses:
            return {
                "message": "I'm here to help. Can you tell me about the emergency?",
                "agent_type": "system",
                "confidence": 0.5,
                "urgency_level": "unknown"
            }
        
        # Priority order: dispatch > guidance > triage > empathy
        priority_order = ["dispatch", "guidance", "triage", "empathy"]
        
        # Find highest priority agent with response
        primary_agent = None
        for agent_type in priority_order:
            if agent_type in agent_responses:
                primary_agent = agent_type
                break
        
        if not primary_agent:
            primary_agent = list(agent_responses.keys())[0]
        
        primary_response = agent_responses[primary_agent]
        
        # Combine empathy with other responses if appropriate
        if primary_agent != "empathy" and "empathy" in agent_responses:
            empathy_response = agent_responses["empathy"]
            # Prepend empathy message to primary response
            primary_response["message"] = f"{empathy_response['message']} {primary_response['message']}"
        
        # Add metadata from all agents
        combined_metadata = {}
        for agent_type, response in agent_responses.items():
            combined_metadata[f"{agent_type}_metadata"] = response.get("metadata", {})
        
        primary_response["metadata"]["all_agents"] = combined_metadata
        
        return primary_response
    
    def _update_session_state(self, session: Dict[str, Any], 
                            agent_responses: Dict[str, Dict[str, Any]]):
        """Update session state based on agent responses"""
        # Update from triage agent
        if "triage" in agent_responses:
            triage_response = agent_responses["triage"]
            metadata = triage_response.get("metadata", {})
            
            if triage_response.get("urgency_level") != "unknown":
                session["urgency_level"] = triage_response["urgency_level"]
            
            if metadata.get("emergency_type"):
                session["emergency_type"] = metadata["emergency_type"]
            
            if metadata.get("critical_keywords"):
                session["critical_keywords"].extend(metadata["critical_keywords"])
                session["critical_keywords"] = list(set(session["critical_keywords"]))  # Remove duplicates
            
            if metadata.get("triage_complete"):
                session["triage_complete"] = True
        
        # Update from dispatch agent
        if "dispatch" in agent_responses:
            dispatch_response = agent_responses["dispatch"]
            metadata = dispatch_response.get("metadata", {})
            
            if metadata.get("dispatch_attempted"):
                session["dispatch_attempted"] = True
            
            if metadata.get("dispatch_successful"):
                session["dispatch_successful"] = True
        
        # Update empathy score
        if "empathy" in agent_responses:
            empathy_metadata = agent_responses["empathy"].get("metadata", {})
            if empathy_metadata.get("empathy_score"):
                session["empathy_score"] = empathy_metadata["empathy_score"]
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of emergency session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "start_time": session["start_time"].isoformat(),
            "duration": str(datetime.utcnow() - session["start_time"]),
            "turn_number": session["turn_number"],
            "urgency_level": session["urgency_level"],
            "emergency_type": session["emergency_type"],
            "triage_complete": session["triage_complete"],
            "dispatch_attempted": session["dispatch_attempted"],
            "dispatch_successful": session["dispatch_successful"],
            "empathy_score": session["empathy_score"],
            "avg_response_time": sum(session["response_times"]) / len(session["response_times"]) if session["response_times"] else 0
        }
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End emergency session and return summary"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        session["end_time"] = datetime.utcnow()
        
        summary = self.get_session_status(session_id)
        summary["total_duration"] = str(session["end_time"] - session["start_time"])
        summary["total_turns"] = session["turn_number"]
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        self.logger.info(f"Ended emergency session: {session_id}")
        
        return summary
