# Flask ADK Agent Server

A production-ready Flask server for deploying Google ADK agents with a conversational web interface. **Works alongside ADK's native web interface** - you can run both simultaneously for different use cases.

## Features

- 🚀 **Real-time Communication**: WebSocket support with fallback to REST API
- 🎨 **Modern UI**: Clean, responsive chat interface with dark mode
- 🔌 **ADK Agent Integration**: Seamless integration with any ADK agent
- 💾 **Session Management**: Persistent conversation history
- 🔒 **Security**: CORS, rate limiting, and security headers
- 📊 **Agent Monitoring**: Real-time connection status and agent info
- 📱 **Mobile Responsive**: Works on all devices
- 🎯 **Production Ready**: Scalable architecture with Redis support
- 🔐 **Google Cloud Auth**: Application Default Credentials (same as Oracle Agent)
- 🌐 **Dual Interface**: Works alongside native ADK web interface

## Architecture

```
flask_agent_server/
├── app.py                 # Main Flask application
├── agent_manager.py       # ADK agent integration layer
├── config.py             # Configuration management
├── run.py                # Multi-interface launcher
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── templates/
│   └── index.html       # Chat interface template
├── static/
│   ├── css/
│   │   └── chat.css     # Styling
│   └── js/
│       └── chat.js      # Frontend logic
└── agents/              # Your ADK agents go here
    └── oracle_agent/    # Example: Oracle agent
```

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo>
cd flask_agent_server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Authentication (Same as Oracle Agent)

The Flask server uses **Application Default Credentials** just like the Oracle Agent:

```bash
# Authenticate with Google Cloud (same as Oracle Agent)
gcloud auth application-default login
gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Agent Configuration
AGENT_PATH=./agents/oracle_agent

# Google Cloud (using Application Default Credentials - same as Oracle Agent)
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STORAGE_BUCKET=your-storage-bucket

# Optional: Redis for production
REDIS_URL=redis://localhost:6379/0
```

### 4. Copy Your Agent

Copy your ADK agent to the `agents` directory:

```bash
cp -r /path/to/your/oracle_agent ./agents/
```

### 5. Run the Interfaces

```bash
# Flask server only
python run.py

# Flask + ADK web in separate terminals (recommended)
python run.py --with-adk

# Or short form
python run.py --adk

# Get help with options
python run.py --help
```

**Available Interfaces:**
- **ADK Web (Native)**: `http://localhost:8000` - Original ADK interface
- **Flask Chat**: `http://localhost:5000` - Conversational web UI  
- **Health Check**: `http://localhost:5000/health` - Server status

**Production mode:**
```bash
FLASK_ENV=production python run.py
```

## Dual Interface Benefits

### 🔮 ADK Web (Native) - `http://localhost:8000`
- **Purpose**: Traditional ADK development and testing
- **Features**: Native ADK interface, direct agent interaction
- **Best for**: Development, debugging, quick agent testing

### 🌐 Flask Chat - `http://localhost:5000`
- **Purpose**: User-friendly conversational interface
- **Features**: Modern chat UI, session management, real-time communication
- **Best for**: End-user interaction, production deployments, demos

### 💡 Use Both Together
```bash
# Launch both interfaces
python run.py --with-adk

# Different use cases:
# → Use ADK Web for agent development and testing
# → Use Flask Chat for user-facing interactions
# → Both connect to the same agent instance
```

## Interface Comparison

| Feature | ADK Web | Flask Chat |
|---------|---------|------------|
| **Purpose** | Development & Testing | User-Facing |
| **UI** | Basic web form | Modern chat interface |
| **Real-time** | Request/Response | WebSocket + REST |
| **Sessions** | Single request | Persistent conversations |
| **Mobile** | Basic | Fully responsive |
| **Production** | Development focus | Production-ready |
| **Agent Access** | Direct | Through agent manager |

## Authentication Setup

### Google Cloud Authentication (Same as Oracle Agent)

This Flask server uses **exactly the same authentication method** as the Oracle Agent:

1. **Install Google Cloud CLI**:
   ```bash
   # Download and install from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate with Application Default Credentials**:
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
   ```

3. **Set Environment Variables** (same as Oracle Agent):
   ```env
   GOOGLE_GENAI_USE_VERTEXAI=true
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_CLOUD_STORAGE_BUCKET=your-storage-bucket
   ```

4. **Verify Authentication**:
   ```bash
   # Check authentication status
   curl http://localhost:5000/api/auth/status
   ```

### Why Application Default Credentials?

- ✅ **Same as Oracle Agent**: Identical authentication method
- ✅ **No Service Account Files**: More secure, no JSON keys to manage
- ✅ **Local Development**: Works seamlessly in development
- ✅ **Production Ready**: Works in Cloud Run, GKE, Compute Engine
- ✅ **Automatic Refresh**: Google handles token refresh

## Agent Integration

### Supported Agent Types

The server automatically detects and supports various ADK agent patterns:

1. **Standard ADK Agents** (LlmAgent, Agent)
2. **Agents with `run()` method**
3. **Agents with `execute()` method**
4. **Async agents** (with `arun()` or `async_run()`)
5. **Callable agents**

### Example Agent Structure

```python
# agents/oracle_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

oracle_agent = LlmAgent(
    name="oracle_agent",
    model="gemini-2.5-pro",
    description="Financial prediction agent",
    instruction="...",
    tools=[...]
)

root_agent = oracle_agent  # Export as root_agent
```

### Custom Agent Wrapper

For complex agents, you can create a wrapper:

```python
# agents/my_agent/wrapper.py
from agent_manager import ADKAgentWrapper

class MyCustomAgent(ADKAgentWrapper):
    def run(self, message: str) -> Dict[str, Any]:
        # Custom processing logic
        result = self.agent.process(message)
        return {'response': result}
```

## Command Line Options

```bash
# Basic usage
python run.py                    # Flask server only
python run.py --with-adk         # Flask + ADK web in separate terminals
python run.py --adk              # Same as --with-adk (short form)
python run.py --flask-only       # Explicitly Flask only
python run.py --help             # Show all options

# Environment control
FLASK_ENV=development python run.py    # Development mode (default)
FLASK_ENV=production python run.py     # Production mode
PORT=8080 python run.py --adk          # Custom Flask port

# Example: Both interfaces with custom port
PORT=8080 python run.py --with-adk
# → ADK Web: http://localhost:8000
# → Flask Chat: http://localhost:8080
```

## API Endpoints

### WebSocket Events

- `connect` - Client connection
- `join_session` - Join a chat session
- `chat_message` - Send a message
- `ping` - Keep-alive ping

### REST API

- `POST /api/chat` - Send a message (fallback)
- `GET /api/sessions/<id>` - Get session history
- `DELETE /api/sessions/<id>` - Clear session
- `GET /health` - Health check with auth status
- `GET /api/auth/status` - Check Google Cloud authentication

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `SECRET_KEY` | Flask secret key | dev-secret-key |
| `AGENT_PATH` | Path to agent directory | ./agents/oracle_agent |
| `AGENT_TIMEOUT` | Agent execution timeout (seconds) | 300 |
| `GOOGLE_GENAI_USE_VERTEXAI` | Use Vertex AI for Gemini | true |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | None |
| `GOOGLE_CLOUD_LOCATION` | Google Cloud region | us-central1 |
| `GOOGLE_CLOUD_STORAGE_BUCKET` | Storage bucket name | None |
| `ALLOWED_ORIGINS` | CORS allowed origins | * |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | false |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute | 20 |
| `REDIS_URL` | Redis URL for sessions | None |
| `LOG_LEVEL` | Logging level | INFO |

## Production Deployment

### 1. Use Production Server

```bash
# Install production dependencies
pip install gunicorn eventlet redis

# Run with Gunicorn
gunicorn -k eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### 2. Enable Redis Sessions

Set `REDIS_URL` in your environment:

```env
REDIS_URL=redis://localhost:6379/0
```

### 3. Configure Nginx (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Use Process Manager

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start app.py --name adk-agent-server --interpreter python
```

## Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install Google Cloud CLI for authentication
RUN apt-get update && apt-get install -y curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update && apt-get install -y google-cloud-cli

EXPOSE 5000

CMD ["gunicorn", "-k", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t adk-agent-server .
docker run -p 5000:5000 --env-file .env adk-agent-server
```

## Customization

### Modify UI Theme

Edit `static/css/chat.css` to customize colors:

```css
:root {
    --primary-color: #2563eb;
    --background: #ffffff;
    /* ... other variables ... */
}
```

### Add Custom Features

1. **New API Endpoints**: Add to `app.py`
2. **Frontend Features**: Modify `static/js/chat.js`
3. **Agent Capabilities**: Update `agent_manager.py`

## Troubleshooting

### Agent Not Loading

1. Check agent path in `.env`
2. Verify agent has `root_agent` or `agent` export
3. Check logs for import errors

### Google Cloud Authentication Issues

1. **Check authentication status**:
   ```bash
   curl http://localhost:5000/api/auth/status
   ```

2. **Re-authenticate if needed**:
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project $GOOGLE_CLOUD_PROJECT
   ```

3. **Verify project settings**:
   ```bash
   gcloud config get-value project
   ```

### WebSocket Connection Issues

1. Ensure eventlet is installed
2. Check firewall/proxy settings
3. Verify CORS configuration

### ADK Web Launch Issues

1. **Windows**: Make sure Command Prompt is available
2. **macOS**: Ensure Terminal app is accessible
3. **Linux**: Install a terminal emulator (gnome-terminal, xterm, etc.)
4. **Manual Launch**: Run `adk web` manually in agent directory

### Session Persistence

1. For production, use Redis
2. Check session timeout settings
3. Verify secret key is set

## Security Considerations

1. **Change Secret Key**: Always use a strong secret key in production
2. **Enable HTTPS**: Use SSL/TLS in production
3. **Rate Limiting**: Enable rate limiting for public deployments
4. **Input Validation**: The server validates all inputs
5. **CORS**: Configure allowed origins properly
6. **Authentication**: Uses Google Cloud Application Default Credentials

## Differences from Standard Flask Deployments

### Oracle Agent Compatibility

This Flask server is specifically designed to work exactly like the Oracle Agent:

- ✅ **Same Authentication**: Application Default Credentials
- ✅ **Same Environment Variables**: GOOGLE_GENAI_USE_VERTEXAI, etc.
- ✅ **Same MCP Integration**: Fi MCP toolset works identically
- ✅ **Same Agent Structure**: Direct compatibility with existing agents

### No Service Account Files Required

Unlike many Flask deployments, this server **does not require**:
- ❌ Service account JSON files
- ❌ GOOGLE_APPLICATION_CREDENTIALS file paths
- ❌ Manual credential management

Instead, it uses the same Google Cloud CLI authentication as ADK.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use in your projects!

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review agent logs
3. Verify authentication with `/api/auth/status`
4. Create an issue on GitHub

---

Built with ❤️ for the ADK community 