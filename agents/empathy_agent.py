import asyncio
import random
from typing import Dict, Any
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .base_agent import BaseAgent, AgentResponse

class EmpathyAgent(BaseAgent):
    """Agent focused on providing emotional support and calming responses"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("EmpathyAgent", config)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Empathic response templates
        self.calming_phrases = [
            "I understand this is scary; I'm here to help you.",
            "You're doing great by calling for help. I'm going to guide you through this.",
            "I know this is overwhelming, but help is on the way. Stay with me.",
            "Take a deep breath. You've done the right thing by calling.",
            "I can hear that you're frightened. That's completely normal. Let me help you.",
            "You're being very brave. I'm here to support you through this.",
            "I understand you're in a difficult situation. We're going to get through this together.",
            "Stay calm. You're not alone. Help is coming."
        ]
        
        self.validation_phrases = [
            "That must be very frightening for you.",
            "I can understand why you're worried.",
            "Your feelings are completely valid.",
            "Anyone would feel scared in this situation.",
            "You're handling this as well as anyone could.",
            "It's natural to feel overwhelmed right now."
        ]
        
        self.reassurance_phrases = [
            "Help is on the way.",
            "You're going to be okay.",
            "Medical professionals will be there soon.",
            "You've taken the right step by calling.",
            "Emergency responders are being dispatched now.",
            "Stay strong - help is coming."
        ]
    
    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message and provide empathic response"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Analyze sentiment
            sentiment_scores = self.sentiment_analyzer.polarity_scores(message)
            sentiment_score = sentiment_scores['compound']
            
            # Determine emotional state
            emotional_state = self._classify_emotional_state(sentiment_scores)
            
            # Generate empathic response
            response_message = self._generate_empathic_response(
                message, emotional_state, sentiment_score, context
            )
            
            # Calculate empathy score
            empathy_score = self._calculate_empathy_score(sentiment_scores)
            
            response_time = asyncio.get_event_loop().time() - start_time
            
            response = AgentResponse(
                message=response_message,
                agent_type="empathy",
                confidence=0.9,
                urgency_level=context.get("urgency_level", "unknown"),
                metadata={
                    "sentiment_score": sentiment_score,
                    "emotional_state": emotional_state,
                    "empathy_score": empathy_score,
                    "response_time": response_time
                }
            )
            
            self.log_interaction(message, response_message, response_time, context)
            
            return response.to_dict()
            
        except Exception as e:
            self.logger.error(f"Error in empathy agent: {str(e)}")
            fallback_response = AgentResponse(
                message="I understand you're in an emergency. Help is on the way. Stay calm.",
                agent_type="empathy",
                confidence=0.5,
                metadata={"error": str(e)}
            )
            return fallback_response.to_dict()
    
    def _classify_emotional_state(self, sentiment_scores: Dict[str, float]) -> str:
        """Classify emotional state based on sentiment analysis"""
        compound = sentiment_scores['compound']
        positive = sentiment_scores['pos']
        negative = sentiment_scores['neg']
        
        if negative > 0.6:
            return "highly_distressed"
        elif negative > 0.3:
            return "distressed"
        elif compound < -0.3:
            return "anxious"
        elif positive > 0.5:
            return "calm"
        else:
            return "neutral"
    
    def _generate_empathic_response(self, message: str, emotional_state: str, 
                                  sentiment_score: float, context: Dict[str, Any]) -> str:
        """Generate appropriate empathic response based on emotional state"""
        
        # Check if this is first contact
        is_first_contact = context.get("turn_number", 0) == 0
        
        if is_first_contact:
            base_response = random.choice(self.calming_phrases)
        else:
            # Choose response based on emotional state
            if emotional_state in ["highly_distressed", "distressed"]:
                base_response = random.choice(self.calming_phrases)
            elif emotional_state == "anxious":
                base_response = random.choice(self.validation_phrases)
            else:
                base_response = random.choice(self.reassurance_phrases)
        
        # Add context-specific elements
        if "pain" in message.lower():
            base_response += " I know you're in pain right now."
        elif "scared" in message.lower() or "afraid" in message.lower():
            base_response += " It's okay to feel scared."
        elif "help" in message.lower():
            base_response += " Help is definitely coming."
        
        # Add breathing instruction for high distress
        if emotional_state == "highly_distressed" and sentiment_score < -0.6:
            base_response += " Try to take slow, deep breaths with me."
        
        return base_response
    
    def _calculate_empathy_score(self, sentiment_scores: Dict[str, float]) -> float:
        """Calculate empathy score based on response appropriateness"""
        # Higher empathy score for appropriate response to negative emotions
        negative_score = sentiment_scores['neg']
        
        if negative_score > 0.5:
            return min(0.9, 0.5 + negative_score * 0.4)  # High empathy for distress
        elif negative_score > 0.2:
            return min(0.7, 0.3 + negative_score * 0.4)  # Moderate empathy
        else:
            return 0.5  # Baseline empathy score
    
    def should_activate(self, context: Dict[str, Any]) -> bool:
        """Determine if empathy agent should be activated"""
        # Always activate for first interaction
        if context.get("turn_number", 0) == 0:
            return True
        
        # Activate if high emotional distress detected
        sentiment_score = context.get("sentiment_score", 0)
        if sentiment_score < -0.3:
            return True
        
        # Activate if caller explicitly asks for support
        message = context.get("message", "").lower()
        support_keywords = ["scared", "afraid", "worried", "nervous", "panic"]
        return any(keyword in message for keyword in support_keywords)
