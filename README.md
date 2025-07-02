<<<<<<< HEAD
# Empathetic-Agent-Eliminating-911-Wait-Times
An Idea of building a agent that works primarily in Eliminating 911 Wait times in Critical Emergency Situations.
=======
# 🚨 Emergency Response Assistant

> **Multi-Agent AI System for Reducing 911 Wait Times**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/Gradio-4.7.1-orange.svg)](https://gradio.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

The Emergency Response Assistant is a cutting-edge multi-agent AI system designed to dramatically reduce 911 wait times by providing immediate, empathetic, and intelligent emergency response assistance. Every second counts in a medical or safety crisis, and our system ensures no caller waits alone.

### 🎯 Key Features

- **🤝 Empathy Agent**: Uses advanced sentiment analysis to provide emotional support with phrases like "I understand this is scary; I'm here to help you"
- **🏥 Triage Agent**: Asks structured questions ("Is anyone unconscious? Are they breathing?") to categorize urgency levels
- **📋 Guidance Agent**: Provides step-by-step life-saving instructions based on verified medical protocols
- **🚑 Dispatch Agent**: Forwards metadata and location to emergency dispatch services

### 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gradio UI     │────│   FastAPI        │────│   Multi-Agent   │
│   (Frontend)    │    │   (Backend)      │    │   Orchestrator  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                        ┌───────────────────────────────┼───────────────────────────────┐
                        │                               │                               │
                ┌───────▼──────┐  ┌────────▼────────┐  ┌───────▼──────┐  ┌──────▼──────┐
                │   Empathy    │  │     Triage      │  │   Guidance   │  │   Dispatch  │
                │    Agent     │  │     Agent       │  │    Agent     │  │    Agent    │
                └──────────────┘  └─────────────────┘  └──────────────┘  └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Windows/macOS/Linux
- 8GB RAM recommended
- Internet connection

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/emergency-response-system.git
cd emergency-response-system
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys (optional for demo)
# OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Test the System

```bash
python test_system.py
```

### 6. Start the Backend API

```bash
python backend/main.py
```

The API will be available at `http://localhost:8000`

### 7. Launch the Gradio Interface

```bash
# Open a new terminal and activate the virtual environment
python frontend/main_gradio.py
```

The interface will be available at `http://localhost:7860`

## 📚 Step-by-Step Setup in VS Code

### 1. Open VS Code

1. Launch Visual Studio Code
2. Open the project folder: `File > Open Folder > emergency_response_system`

### 2. Set Up Python Environment

1. Open Command Palette: `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type: "Python: Select Interpreter"
3. Choose the virtual environment interpreter: `./venv/Scripts/python.exe` (Windows) or `./venv/bin/python` (Mac/Linux)

### 3. Install Extensions (Recommended)

- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Python Debugger** (Microsoft)
- **autoDocstring** (Nils Werner)

### 4. Open Integrated Terminal

1. Press `Ctrl+`` (backtick) to open terminal
2. Ensure virtual environment is activated (you should see `(venv)` in terminal)

### 5. Run the Test Suite

```bash
python test_system.py
```

### 6. Start Backend (Terminal 1)

```bash
python backend/main.py
```

### 7. Start Frontend (Terminal 2)

Open a new terminal tab (`Ctrl+Shift+``) and run:

```bash
python frontend/main_gradio.py
```

## 🧪 Testing Examples

Try these emergency scenarios in the interface:

### Critical Medical Emergency
```
User: "Someone is unconscious and not breathing!"
Expected: Empathy + Triage agents activate, CPR guidance provided
```

### Fire Emergency
```
User: "There's a fire in my kitchen!"
Expected: High urgency classification, fire safety instructions
```

### Chest Pain
```
User: "I'm having severe chest pain"
Expected: Medical triage, heart attack protocol guidance
```

## 📊 System Components

### 🤝 Empathy Agent
- **Purpose**: Emotional support and calming responses
- **Technology**: VADER Sentiment Analysis
- **Features**: 
  - Real-time emotional state classification
  - Context-aware empathetic responses
  - Breathing guidance for high distress

### 🏥 Triage Agent
- **Purpose**: Emergency classification and information gathering
- **Features**:
  - Keyword-based urgency assessment
  - Structured questioning protocol
  - Critical information extraction

### 📋 Guidance Agent
- **Purpose**: Life-saving instruction delivery
- **Features**:
  - Evidence-based medical protocols
  - Step-by-step guidance for CPR, choking, bleeding control
  - Scenario-specific instructions

### 🚑 Dispatch Agent
- **Purpose**: Emergency service coordination
- **Features**:
  - Mock dispatch system integration
  - Priority classification
  - Location and metadata forwarding

## 🔧 API Documentation

### Start Session
```http
POST /sessions/start
Content-Type: application/json

{
  "caller_info": {
    "phone": "123-456-7890",
    "address": "123 Main St"
  }
}
```

### Send Message
```http
POST /sessions/{session_id}/message
Content-Type: application/json

{
  "session_id": "uuid-here",
  "message": "Someone is unconscious"
}
```

### Get Session Status
```http
GET /sessions/{session_id}/status
```

## 📈 Performance Metrics

The system tracks several key metrics:

- **Response Time**: Average time for agent responses
- **Empathy Score**: Sentiment-based empathy measurement (0.0-1.0)
- **Triage Accuracy**: Correctness of urgency classification
- **Resolution Time**: Time to complete emergency assessment

## 🛡️ Safety Features

### Safety Monitoring
- **Profanity Filtering**: Automatic content moderation
- **Loop Breaker**: Prevents infinite conversations
- **Safety Keywords**: Special handling for suicide/self-harm mentions
- **Session Limits**: Maximum conversation turns

### Privacy Protection
- **Data Anonymization**: Personal information is anonymized
- **Secure Storage**: All data encrypted at rest
- **Audit Logging**: Complete conversation audit trails

## 📋 Development Phases

### ✅ Phase 1: Text-Only MVP
- [x] Multi-agent architecture
- [x] Gradio chat interface
- [x] FastAPI backend
- [x] SQLite database
- [x] Basic analytics

### 🔄 Phase 2: Voice Integration (Future)
- [ ] Twilio voice API integration
- [ ] Speech-to-text (ASR)
- [ ] Text-to-speech (TTS)
- [ ] Real-time voice processing

### 📊 Phase 3: Advanced Analytics (Future)
- [ ] Plotly Dash dashboard
- [ ] Panel safety analytics
- [ ] Real-time metrics
- [ ] Performance optimization

## 🏗️ Project Structure

```
emergency_response_system/
├── 📁 agents/                  # AI agent implementations
│   ├── base_agent.py          # Base agent class
│   ├── empathy_agent.py       # Empathy agent
│   ├── triage_agent.py        # Triage agent
│   ├── guidance_agent.py      # Guidance agent
│   ├── dispatch_agent.py      # Dispatch agent
│   └── orchestrator.py        # Multi-agent coordinator
├── 📁 backend/                 # FastAPI backend
│   ├── main.py                # API server
│   └── models.py              # Database models
├── 📁 config/                  # Configuration
│   └── config.py              # App configuration
├── 📁 frontend/                # User interfaces
│   └── main_gradio.py         # Gradio chat interface
├── 📁 dashboard/               # Analytics (future)
├── 📁 data/                    # Data storage
├── requirements.txt            # Python dependencies
├── test_system.py             # Test suite
├── .env.example               # Environment template
└── README.md                  # This file
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add unit tests for new features
- Update documentation
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**This is a demonstration system for educational and research purposes only. In a real emergency, always call 911 or your local emergency number immediately.**

This system is not intended to replace professional emergency services and should not be relied upon for actual emergency response.

## 🙏 Acknowledgments

- **Emergency Medical Protocols**: Based on American Heart Association guidelines
- **Sentiment Analysis**: VADER (Valence Aware Dictionary and sEntiment Reasoner)
- **UI Framework**: Gradio for rapid prototyping
- **Backend Framework**: FastAPI for high-performance APIs

## 📞 Support

For questions and support:

- 📧 Email: support@emergency-response-ai.com
- 💬 Discord: [Join our community](https://discord.gg/emergency-ai)
- 📖 Documentation: [Read the docs](https://docs.emergency-response-ai.com)

---

**Built with ❤️ for saving lives through technology**
>>>>>>> 0a2279d (Initial commit)
