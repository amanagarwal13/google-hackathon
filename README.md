# Google Hackathon - Financial AI Agent System

A financial AI agent system built with ADK (Agent Development Kit) and Flask, featuring Oracle Agent, Tax Advisor Agent, and Parallel Universe Agent for comprehensive financial analysis and planning.

## Project Structure

```
google-hackathon/
├── flask_agent_server2/          # Flask web server for agent communication
│   ├── app.py                   # Main Flask application
│   ├── agent_manager.py         # ADK agent integration layer
│   ├── config.py               # Configuration management
│   ├── requirements.txt        # Python dependencies
│   ├── templates/              # HTML templates
│   ├── static/                 # CSS, JS assets
│   ├── oracle_agent/           # Oracle financial agent
│   ├── tax_advisor_agent/      # Tax planning agent  
│   └── parallel_universe_agent/ # Scenario analysis agent
├── oracle_agent/               # Standalone Oracle agent
├── tax_advisor_agent/          # Standalone Tax advisor
├── parallel_universe_agent/    # Standalone Parallel universe agent
└── README.md                   # This file
```

## Features

- 🔮 **Oracle Agent**: Financial prediction and analysis
- 💰 **Tax Advisor Agent**: Tax planning and optimization
- 🌌 **Parallel Universe Agent**: Scenario modeling and insights
- 🚀 **Real-time Communication**: WebSocket support with web interface
- 🎨 **Modern UI**: Clean, responsive chat interface
- 🔐 **Google Cloud Integration**: Uses ADK authentication
- 📊 **Multi-Agent System**: Coordinated financial intelligence

## Quick Start

### Prerequisites

1. **Google Cloud CLI** installed and authenticated
2. **Python 3.8+** installed
3. **ADK (Agent Development Kit)** installed

### Setup Instructions

This project requires **two terminals** to run properly:

#### Terminal 1: ADK Web Interface
```bash
# Navigate to the main project directory
cd google-hackathon

# Run ADK web interface
adk web
```

#### Terminal 2: Flask Agent Server
```bash
# Navigate to the Flask server directory
cd google-hackathon/flask_agent_server2

# Create and activate virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

### Google Cloud Authentication

The system uses Google Cloud Application Default Credentials (same as ADK):

```bash
# Authenticate with Google Cloud
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

### Environment Configuration

Create a `.env` file in the `flask_agent_server2` directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Google Cloud Configuration
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Agent Configuration
AGENT_TIMEOUT=300
```

## How It Works

### Dual-Terminal Architecture

1. **Terminal 1 (ADK Web)**: 
   - Runs from `google-hackathon/` directory
   - Provides the main ADK web interface
   - Handles agent development and testing

2. **Terminal 2 (Flask Server)**:
   - Runs from `flask_agent_server2/` directory  
   - Provides web API for agent communication
   - Serves the chat interface at `http://localhost:5000`

### Agent Communication

The Flask server acts as a bridge between the web interface and the ADK agents:
- Loads agents from the local directories
- Provides REST API and WebSocket endpoints
- Manages conversation sessions
- Handles real-time agent responses

## Available Agents

### Oracle Agent
- **Location**: `oracle_agent/` and `flask_agent_server2/oracle_agent/`
- **Purpose**: Financial analysis and prediction
- **Sub-agents**: Financial analyzer, health score calculator, future simulator, scenario modeler, timeline predictor

### Tax Advisor Agent  
- **Location**: `tax_advisor_agent/` and `flask_agent_server2/tax_advisor_agent/`
- **Purpose**: Tax planning and optimization
- **Sub-agents**: Tax analyzer, planner, deduction optimizer, scenario modeler

### Parallel Universe Agent
- **Location**: `parallel_universe_agent/` and `flask_agent_server2/parallel_universe_agent/`
- **Purpose**: Alternative scenario analysis
- **Sub-agents**: Insight synthesizer

## API Endpoints

### WebSocket Events
- `connect` - Client connection
- `join_session` - Join a chat session  
- `chat_message` - Send a message
- `ping` - Keep-alive ping

### REST API
- `POST /api/chat` - Send a message
- `GET /api/sessions/<id>` - Get session history
- `DELETE /api/sessions/<id>` - Clear session
- `GET /health` - Health check
- `GET /api/auth/status` - Check authentication

## Development Workflow

1. **Start ADK Web** (Terminal 1):
   ```bash
   cd google-hackathon
   adk web
   ```

2. **Start Flask Server** (Terminal 2):
   ```bash
   cd google-hackathon/flask_agent_server2
   python app.py
   ```

3. **Access Interfaces**:
   - ADK Web: Follow the URL shown in Terminal 1
   - Flask Chat: `http://localhost:5000`

## Troubleshooting

### Agent Not Loading
1. Check that both terminals are running
2. Verify agent paths in the Flask server
3. Check logs in both terminals for errors

### Authentication Issues
1. Re-authenticate with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```
2. Check project configuration:
   ```bash
   gcloud config get-value project
   ```

### Port Conflicts
- ADK web typically uses port 8000
- Flask server uses port 5000  
- Ensure both ports are available

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes to the appropriate agent directory
4. Test with both ADK web and Flask server
5. Submit a pull request

## License

MIT License - Built for Google Hackathon

---

🚀 **Ready to explore financial AI?** Start both terminals and begin your journey! 