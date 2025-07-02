import asyncio
import re
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent, AgentResponse

class TriageAgent(BaseAgent):
    """Agent for categorizing emergency urgency and gathering critical information"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("TriageAgent", config)
        
        # Critical keywords by category
        self.critical_medical = [
            "unconscious", "not breathing", "no pulse", "chest pain", "heart attack",
            "stroke", "seizure", "severe bleeding", "choking", "overdose"
        ]
        
        self.critical_safety = [
            "fire", "smoke", "explosion", "gun", "weapon", "assault", "violence",
            "robbery", "break in", "intruder", "domestic violence"
        ]
        
        self.high_priority = [
            "difficulty breathing", "severe pain", "heavy bleeding", "broken bone",
            "car accident", "fall", "burn", "allergic reaction", "pregnancy"
        ]
        
        self.medium_priority = [
            "moderate pain", "minor bleeding", "nausea", "fever", "rash",
            "anxiety", "panic attack", "minor injury"
        ]
        
        # Structured triage questions
        self.triage_questions = {
            "consciousness": "Is the person conscious and able to respond?",
            "breathing": "Is the person breathing normally?",
            "bleeding": "Is there any severe bleeding?",
            "pain_level": "On a scale of 1-10, how severe is the pain?",
            "location": "What is your exact location?",
            "age": "What is the person's approximate age?",
            "medical_history": "Any known medical conditions or allergies?",
            "what_happened": "Can you briefly describe what happened?"
        }
        
        # Response protocols
        self.protocol_responses = {
            "critical": "This is a critical emergency. Emergency responders are being dispatched immediately.",
            "high": "This requires urgent medical attention. Help is on the way.",
            "medium": "Medical assistance is needed. Emergency services will respond promptly.",
            "low": "We'll send appropriate help. Please stay on the line."
        }
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message for triage assessment"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Extract key information
            urgency_level, emergency_type = self._assess_urgency(message)
            critical_keywords = self._extract_critical_keywords(message)
            
            # Determine next question or action
            response_message = self._generate_triage_response(
                message, urgency_level, emergency_type, context
            )
            
            # Calculate confidence based on information gathered
            confidence = self._calculate_confidence(context)
            
            response_time = asyncio.get_event_loop().time() - start_time
            
            response = AgentResponse(
                message=response_message,
                agent_type="triage",
                confidence=confidence,
                urgency_level=urgency_level,
                metadata={
                    "emergency_type": emergency_type,
                    "critical_keywords": critical_keywords,
                    "triage_complete": self._is_triage_complete(context),
                    "response_time": response_time,
                    "questions_asked": context.get("questions_asked", [])
                }
            )
            
            self.log_interaction(message, response_message, response_time, context)
            
            return response.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error in triage agent: {str(e)}")
            fallback_response = AgentResponse(
                message="I need to gather some important information. Are you or someone else injured?",
                agent_type="triage",
                confidence=0.5,
                urgency_level="unknown",
                metadata={"error": str(e)}
            )
            return fallback_response.to_dict()
    
    def _assess_urgency(self, message: str) -> Tuple[str, str]:
        """Assess urgency level and emergency type from message"""
        message_lower = message.lower()
        
        # Check for critical medical emergencies
        critical_medical_found = [kw for kw in self.critical_medical if kw in message_lower]
        if critical_medical_found:
            return "critical", "medical"
        
        # Check for critical safety emergencies
        critical_safety_found = [kw for kw in self.critical_safety if kw in message_lower]
        if critical_safety_found:
            return "critical", "safety"
        
        # Check for high priority
        high_priority_found = [kw for kw in self.high_priority if kw in message_lower]
        if high_priority_found:
            emergency_type = "medical" if any(kw in ["breathing", "pain", "bleeding", "accident"] 
                                            for kw in high_priority_found) else "safety"
            return "high", emergency_type
        
        # Check for medium priority
        medium_priority_found = [kw for kw in self.medium_priority if kw in message_lower]
        if medium_priority_found:
            return "medium", "medical"
        
        # Default assessment
        if any(word in message_lower for word in ["police", "crime", "theft"]):
            return "medium", "police"
        elif any(word in message_lower for word in ["fire", "smoke"]):
            return "high", "fire"
        else:
            return "unknown", "unknown"
    
    def _extract_critical_keywords(self, message: str) -> List[str]:
        """Extract all critical keywords from message"""
        all_critical = self.critical_medical + self.critical_safety + self.high_priority
        return self.extract_keywords(message, all_critical)
    
    def _generate_triage_response(self, message: str, urgency_level: str, 
                                emergency_type: str, context: Dict[str, Any]) -> str:
        """Generate appropriate triage response and next question"""
        
        questions_asked = context.get("questions_asked", [])
        
        # First, acknowledge the urgency level
        protocol_message = self.protocol_responses.get(urgency_level, "")
        
        # Determine next critical question to ask
        next_question = self._get_next_critical_question(
            urgency_level, emergency_type, questions_asked, message
        )
        
        if next_question:
            if protocol_message:
                return f"{protocol_message} {next_question}"
            else:
                return next_question
        else:
            # Triage complete
            return f"{protocol_message} I have enough information to dispatch appropriate help."
    
    def _get_next_critical_question(self, urgency_level: str, emergency_type: str,
                                   questions_asked: List[str], message: str) -> str:
        """Determine the next most critical question to ask"""
        
        message_lower = message.lower()
        
        # Critical questions in order of priority
        if urgency_level == "critical":
            if "consciousness" not in questions_asked:
                if not any(word in message_lower for word in ["conscious", "awake", "responding"]):
                    return self.triage_questions["consciousness"]
            
            if "breathing" not in questions_asked:
                if not any(word in message_lower for word in ["breathing", "breath", "air"]):
                    return self.triage_questions["breathing"]
            
            if "bleeding" not in questions_asked:
                if not any(word in message_lower for word in ["bleeding", "blood"]):
                    return self.triage_questions["bleeding"]
        
        # Location is always critical if not provided
        if "location" not in questions_asked:
            if not any(word in message_lower for word in ["address", "street", "location", "where"]):
                return self.triage_questions["location"]
        
        # What happened if not clear
        if "what_happened" not in questions_asked:
            if len(message.split()) < 5:  # Very brief message
                return self.triage_questions["what_happened"]
        
        # Age for medical emergencies
        if emergency_type == "medical" and "age" not in questions_asked:
            if not any(word in message_lower for word in ["old", "age", "year"]):
                return self.triage_questions["age"]
        
        # Pain level for medical emergencies with pain
        if "pain" in message_lower and "pain_level" not in questions_asked:
            return self.triage_questions["pain_level"]
        
        return ""  # No more critical questions needed
    
    def _is_triage_complete(self, context: Dict[str, Any]) -> bool:
        """Check if enough information has been gathered for triage"""
        questions_asked = context.get("questions_asked", [])
        urgency_level = context.get("urgency_level", "unknown")
        
        # Minimum requirements for triage completion
        required_questions = ["location", "what_happened"]
        
        if urgency_level == "critical":
            required_questions.extend(["consciousness", "breathing"])
        
        return all(q in questions_asked for q in required_questions)
    
    def _calculate_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence in triage assessment"""
        questions_asked = len(context.get("questions_asked", []))
        urgency_level = context.get("urgency_level", "unknown")
        
        base_confidence = 0.3
        question_bonus = min(questions_asked * 0.15, 0.6)
        
        if urgency_level != "unknown":
            urgency_bonus = 0.2
        else:
            urgency_bonus = 0.0
        
        return min(base_confidence + question_bonus + urgency_bonus, 1.0)
    
    def should_activate(self, context: Dict[str, Any]) -> bool:
        """Determine if triage agent should be activated"""
        # Always activate if triage not complete
        if not self._is_triage_complete(context):
            return True
        
        # Activate if urgency level needs reassessment
        urgency_level = context.get("urgency_level", "unknown")
        if urgency_level == "unknown":
            return True
        
        return False
