from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import logging
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all emergency response agents"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"Agent.{name}")
        self.response_time_threshold = config.get("MAX_RESPONSE_TIME", 30)
        
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message and return response"""
        pass
    
    def log_interaction(self, user_message: str, agent_response: str, 
                       response_time: float, context: Dict[str, Any]):
        """Log agent interaction for analytics"""
        self.logger.info(f"Agent: {self.name}")
        self.logger.info(f"User: {user_message[:100]}...")
        self.logger.info(f"Response: {agent_response[:100]}...")
        self.logger.info(f"Response Time: {response_time:.2f}s")
        
    def validate_response_time(self, response_time: float) -> bool:
        """Check if response time is within acceptable limits"""
        return response_time <= self.response_time_threshold
    
    def extract_keywords(self, text: str, keyword_list: list) -> list:
        """Extract matching keywords from text"""
        text_lower = text.lower()
        found_keywords = []
        for keyword in keyword_list:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        return found_keywords
    
    def calculate_urgency_score(self, keywords: list, sentiment_score: float) -> float:
        """Calculate urgency score based on keywords and sentiment"""
        keyword_weight = len(keywords) * 0.3
        sentiment_weight = abs(sentiment_score) * 0.7
        return min(keyword_weight + sentiment_weight, 1.0)

class AgentResponse:
    """Standardized agent response format"""
    
    def __init__(self, message: str, agent_type: str, confidence: float = 1.0,
                 urgency_level: str = "unknown", metadata: Dict[str, Any] = None):
        self.message = message
        self.agent_type = agent_type
        self.confidence = confidence
        self.urgency_level = urgency_level
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "agent_type": self.agent_type,
            "confidence": self.confidence,
            "urgency_level": self.urgency_level,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }
