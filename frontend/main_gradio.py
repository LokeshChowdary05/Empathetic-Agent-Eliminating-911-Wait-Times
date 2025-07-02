# Text-only MVP via Gradio for emergency response system
import gradio as gr
import requests
import json
from typing import List, Tuple

BASE_API_URL = "http://localhost:8000"

# Global session storage
current_session_id = None

def start_new_session(caller_phone: str) -> Tuple[List[Tuple[str, str]], str]:
    """Start a new emergency session"""
    global current_session_id
    
    try:
        caller_info = {"phone": caller_phone} if caller_phone else None
        response = requests.post(f"{BASE_API_URL}/sessions/start", json={"caller_info": caller_info})
        
        if response.status_code == 200:
            data = response.json()
            current_session_id = data.get("session_id")
            
            # Return initial chat with system message
            initial_chat = [(
                "System", 
                f"🚨 Emergency Response Assistant activated. Session ID: {current_session_id[:8]}...\n\n" +
                "I'm here to help you with your emergency. Please tell me what's happening."
            )]
            
            return initial_chat, "Session started successfully. You can now send messages."
        else:
            return [], f"Error starting session: {response.text}"
            
    except Exception as e:
        return [], f"Error connecting to server: {str(e)}"

def send_message(chat_history: List[Tuple[str, str]], user_message: str) -> Tuple[List[Tuple[str, str]], str]:
    """Send message to emergency response system"""
    global current_session_id
    
    if not current_session_id:
        return chat_history, "Please start a session first."
    
    if not user_message.strip():
        return chat_history, ""
    
    try:
        # Send message to API
        response = requests.post(
            f"{BASE_API_URL}/sessions/{current_session_id}/message",
            json={"session_id": current_session_id, "message": user_message}
        )
        
        if response.status_code == 200:
            data = response.json()
            agent_response = data.get("message", "No response received")
            agent_type = data.get("agent_type", "system")
            urgency = data.get("urgency_level", "unknown")
            confidence = data.get("confidence", 0.0)
            
            # Format agent response with metadata
            formatted_response = f"**{agent_type.title()} Agent** (Urgency: {urgency}, Confidence: {confidence:.1f})\n\n{agent_response}"
            
            # Add to chat history
            chat_history.append((user_message, formatted_response))
            
            return chat_history, ""
        else:
            error_msg = f"Error: {response.text}"
            chat_history.append((user_message, error_msg))
            return chat_history, ""
            
    except Exception as e:
        error_msg = f"Connection error: {str(e)}"
        chat_history.append((user_message, error_msg))
        return chat_history, ""

def get_session_status() -> str:
    """Get current session status"""
    global current_session_id
    
    if not current_session_id:
        return "No active session"
    
    try:
        response = requests.get(f"{BASE_API_URL}/sessions/{current_session_id}/status")
        
        if response.status_code == 200:
            data = response.json()
            return f"""📊 **Session Status**
- Session ID: {current_session_id[:8]}...
- Duration: {data.get('duration', 'Unknown')}
- Turn Number: {data.get('turn_number', 0)}
- Urgency Level: {data.get('urgency_level', 'unknown')}
- Emergency Type: {data.get('emergency_type', 'unknown')}
- Triage Complete: {data.get('triage_complete', False)}
- Empathy Score: {data.get('empathy_score', 0.0):.2f}
- Avg Response Time: {data.get('avg_response_time', 0.0):.2f}s"""
        else:
            return f"Error getting status: {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def end_current_session() -> str:
    """End the current session"""
    global current_session_id
    
    if not current_session_id:
        return "No active session to end"
    
    try:
        response = requests.post(f"{BASE_API_URL}/sessions/{current_session_id}/end")
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get('summary', {})
            session_id = current_session_id
            current_session_id = None
            
            return f"""✅ **Session Ended**
- Session ID: {session_id[:8]}...
- Total Duration: {summary.get('total_duration', 'Unknown')}
- Total Turns: {summary.get('total_turns', 0)}
- Final Urgency: {summary.get('urgency_level', 'unknown')}
- Emergency Type: {summary.get('emergency_type', 'unknown')}
- Final Empathy Score: {summary.get('empathy_score', 0.0):.2f}"""
        else:
            return f"Error ending session: {response.text}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Emergency Response Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
        # 🚨 Emergency Response Assistant
        
        **Multi-Agent Emergency Response System** - Reducing 911 Wait Times Through AI
        
        This system combines multiple AI agents:
        - 🤝 **Empathy Agent**: Provides emotional support and calming responses
        - 🏥 **Triage Agent**: Assesses urgency and gathers critical information
        - 📋 **Guidance Agent**: Provides step-by-step emergency instructions
        - 🚑 **Dispatch Agent**: Coordinates with emergency services
        
        ⚠️ **This is a demonstration system. In a real emergency, call 911 immediately.**
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            # Session management
            gr.Markdown("### 📞 Start Emergency Session")
            phone_input = gr.Textbox(
                label="Phone Number (Optional)",
                placeholder="123-456-7890",
                info="Enter your phone number to start a session"
            )
            start_btn = gr.Button("🚨 Start Emergency Call", variant="primary")
            session_status = gr.Textbox(label="Session Status", interactive=False)
            
            # Chat interface
            gr.Markdown("### 💬 Emergency Chat")
            chatbot = gr.Chatbot(
                label="Emergency Response Assistant",
                height=400,
                show_label=True
            )
            
            with gr.Row():
                message_input = gr.Textbox(
                    label="Your Message",
                    placeholder="Describe your emergency...",
                    scale=4
                )
                send_btn = gr.Button("Send", variant="secondary", scale=1)
            
        with gr.Column(scale=1):
            # Session controls and status
            gr.Markdown("### 📊 Session Controls")
            status_btn = gr.Button("📈 Get Session Status")
            status_output = gr.Markdown("No active session")
            
            end_btn = gr.Button("❌ End Session", variant="stop")
            end_output = gr.Textbox(label="Session End Result", interactive=False)
            
            gr.Markdown(
                """
                ### 🆘 Quick Emergency Examples
                
                Try these example emergencies:
                
                - "Someone is unconscious and not breathing"
                - "There's a fire in my kitchen"
                - "I'm having severe chest pain"
                - "Someone is choking"
                - "Car accident on Highway 101"
                """
            )
    
    # Event handlers
    start_btn.click(
        fn=start_new_session,
        inputs=[phone_input],
        outputs=[chatbot, session_status]
    )
    
    send_btn.click(
        fn=send_message,
        inputs=[chatbot, message_input],
        outputs=[chatbot, message_input]
    )
    
    message_input.submit(
        fn=send_message,
        inputs=[chatbot, message_input],
        outputs=[chatbot, message_input]
    )
    
    status_btn.click(
        fn=get_session_status,
        outputs=[status_output]
    )
    
    end_btn.click(
        fn=end_current_session,
        outputs=[end_output]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )

