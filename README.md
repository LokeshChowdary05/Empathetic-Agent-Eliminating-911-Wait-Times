# Empathetic-Agent-Eliminating-911-Wait-Times

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


**Built with ❤️ for saving lives through technology**
Feel Free to email : lokeshchowdary.pl@gmail.com
