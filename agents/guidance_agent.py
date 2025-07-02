import asyncio
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentResponse


class GuidanceAgent(BaseAgent):
    """Agent responsible for providing step-by-step emergency instructions"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__("GuidanceAgent", config)

        # Guidance instructions categorized by type of emergency
        self.guidance_protocols = {
            "unconscious_not_breathing": "Place the person on their back on a firm surface. Place the heel of one hand on the center of their chest, and your other hand on top of the first. Keep your elbows straight and position your shoulders directly above your hands. Use your body weight to help you administer compressions at least 2 inches deep and delivered at a rate of at least 100 compressions per minute.",
            "choking": "Stand behind the person and slightly to one side. Support their chest with one hand. Give up to five sharp blows between the person’s shoulder blades with the heel of your hand.",
            "bleeding": "If bleeding won’t stop after 10 minutes of firm and steady pressure: apply more bandages and dressing without lifting the first one. Keep applying pressure until help arrives.",
            "chest_pain": "Have the person sit down and rest. If they have prescribed nitroglycerin, help them take it. Loosen any tight clothing. Stay with them until help arrives.",
            "stroke": "Note the time symptoms started. Have the person lie down with head and shoulders slightly raised. Do not give food or water. Monitor breathing.",
            "seizure": "Do not restrain the person. Clear the area of hard objects. Place something soft under their head. Time the seizure. Do not put anything in their mouth.",
            "burn": "Cool the burn with cool (not cold) running water for 10-20 minutes. Remove any jewelry or tight items before swelling begins. Cover with a clean, dry cloth.",
            "fracture": "Do not move the injured area. Immobilize the area above and below the fracture. Apply ice wrapped in a cloth to reduce swelling.",
            "allergic_reaction": "If the person has an epinephrine auto-injector (EpiPen), help them use it. Have them lie down with legs elevated. Monitor breathing closely."
        }

        # Guidance questions categorized by type
        self.guidance_questions = {
            "consciousness": "Is the person responsive? Can you wake them by gently shaking their shoulders?",
            "breathing": "Is the person breathing on their own yet?",
            "bleeding_control": "Is the bleeding under control after applying pressure?",
            "obstruction_clear": "Has the obstruction been cleared from the airway?"
        }

    async def process_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process message to give step-by-step guidance"""
        start_time = asyncio.get_event_loop().time()

        try:
            # Determine emergency scenario
            guidance_needed = self._determine_guidance_needed(context)

            # Generate guidance response
            response_message = self._generate_guidance_response(guidance_needed, context)

            response_time = asyncio.get_event_loop().time() - start_time

            response = AgentResponse(
                message=response_message,
                agent_type="guidance",
                confidence=0.95,
                urgency_level=context.get("urgency_level", "unknown"),
                metadata={
                    "guidance_needed": guidance_needed,
                    "guidance_provided": guidance_needed in response_message,
                    "response_time": response_time
                }
            )

            self.log_interaction(message, response_message, response_time, context)

            return response.to_dict()

        except Exception as e:
            self.logger.error(f"Error in guidance agent: {str(e)}")
            fallback_response = AgentResponse(
                message="Let me provide some guidance until help arrives. Ensure that everyone stays safe.",
                agent_type="guidance",
                confidence=0.5,
                metadata={"error": str(e)}
            )
            return fallback_response.to_dict()

    def _determine_guidance_needed(self, context: Dict[str, Any]) -> str:
        """Determine what guidance is needed based on context"""
        urgency_level = context.get("urgency_level", "unknown")
        emergency_type = context.get("emergency_type", "unknown")
        critical_keywords = context.get("critical_keywords", [])
        
        # Map keywords to guidance protocols
        keyword_mapping = {
            "unconscious": "unconscious_not_breathing",
            "not breathing": "unconscious_not_breathing",
            "choking": "choking",
            "bleeding": "bleeding",
            "severe bleeding": "bleeding",
            "chest pain": "chest_pain",
            "heart attack": "chest_pain",
            "stroke": "stroke",
            "seizure": "seizure",
            "burn": "burn",
            "broken bone": "fracture",
            "allergic reaction": "allergic_reaction"
        }
        
        # Check for specific keywords first
        for keyword in critical_keywords:
            if keyword.lower() in keyword_mapping:
                return keyword_mapping[keyword.lower()]
        
        # Fall back to emergency type
        if urgency_level == "critical" and emergency_type == "medical":
            return "unconscious_not_breathing"  # Default critical medical
        
        return "unknown"

    def _generate_guidance_response(self, guidance_needed: str, context: Dict[str, Any]) -> str:
        """Generate guidance instructions based on the identified need"""
        urgency_level = context.get("urgency_level", "unknown")
        
        # Provide specific guidance if protocol exists
        if guidance_needed in self.guidance_protocols:
            protocol_text = self.guidance_protocols[guidance_needed]
            return f"Here's what you need to do right now: {protocol_text} Continue until emergency responders arrive."
        
        # Provide general guidance based on urgency
        if urgency_level == "critical":
            return "Keep the person as comfortable as possible. Monitor their breathing and consciousness. Do not move them unless they are in immediate danger. Emergency responders are on their way."
        elif urgency_level == "high":
            return "Try to keep the person calm and comfortable. Apply basic first aid if you know how. Help is coming soon."
        else:
            return "Stay with the person and keep them comfortable until help arrives. Monitor their condition and be ready to provide updates to emergency responders."
    
    def should_activate(self, context: Dict[str, Any]) -> bool:
        """Determine if guidance agent should be activated"""
        urgency_level = context.get("urgency_level", "unknown")
        critical_keywords = context.get("critical_keywords", [])
        
        # Activate for critical emergencies
        if urgency_level in ["critical", "high"]:
            return True
        
        # Activate if specific guidance keywords present
        guidance_keywords = ["bleeding", "choking", "unconscious", "chest pain", "seizure"]
        return any(keyword in critical_keywords for keyword in guidance_keywords)

