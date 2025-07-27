"""
Flask Server for ADK Agent Deployment
Acts as a proxy to ADK server and provides web interface
"""

from flask import Flask, render_template, request, jsonify, session, send_from_directory, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import uuid
import os
import logging
from datetime import datetime
import json
import requests
from typing import Dict, Any, Optional

from config import Config, setup_google_cloud_auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup Google Cloud authentication
setup_google_cloud_auth()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app, resources={r"/*": {"origins": Config.ALLOWED_ORIGINS}})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# ADK API Configuration
ADK_BASE_URL = os.environ.get('ADK_BASE_URL', 'http://localhost:8000')
ADK_TIMEOUT = int(os.environ.get('ADK_TIMEOUT', '300'))

# Session store for web UI (in production, use Redis)
active_sessions = {}


class ADKClient:
    """ADK API client with proper error handling"""
    
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def request(self, method, endpoint, **kwargs):
        """Make a request to ADK server"""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault('timeout', ADK_TIMEOUT)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"ADK API request failed: {e}")
            raise


# Initialize ADK client
adk_client = ADKClient(ADK_BASE_URL)


def ensure_adk_session(app_name, user_id, session_id):
    """Ensure session exists in ADK before running agent"""
    try:
        # First check if session exists
        try:
            response = adk_client.request('GET', f'/apps/{app_name}/users/{user_id}/sessions/{session_id}')
            logger.info(f"Session {session_id} already exists for user {user_id}")
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Session doesn't exist, create it
                logger.info(f"Creating new session {session_id} for user {user_id}")
                create_response = adk_client.request(
                    'POST',
                    f'/apps/{app_name}/users/{user_id}/sessions/{session_id}',
                    json={"additionalProp1": {}}
                )
                logger.info(f"Session created successfully: {create_response.status_code}")
                return True
            else:
                logger.error(f"Error checking session: {e}")
                raise
    except Exception as e:
        logger.error(f"Failed to ensure ADK session: {e}")
        raise


# ===== ADK API Proxy Endpoints =====

@app.route('/list-apps', methods=['GET'])
def list_apps():
    """Proxy to ADK list-apps endpoint"""
    try:
        response = adk_client.request('GET', '/list-apps')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/apps/<app_name>/users/<user_id>/sessions', methods=['GET'])
def list_sessions(app_name, user_id):
    """Proxy to ADK list sessions endpoint"""
    try:
        response = adk_client.request('GET', f'/apps/{app_name}/users/{user_id}/sessions')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/apps/<app_name>/users/<user_id>/sessions', methods=['POST'])
def create_session(app_name, user_id):
    """Proxy to ADK create session endpoint"""
    try:
        response = adk_client.request(
            'POST', 
            f'/apps/{app_name}/users/{user_id}/sessions',
            json=request.json or {}
        )
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/apps/<app_name>/users/<user_id>/sessions/<session_id>', methods=['GET'])
def get_session(app_name, user_id, session_id):
    """Proxy to ADK get session endpoint"""
    try:
        response = adk_client.request('GET', f'/apps/{app_name}/users/{user_id}/sessions/{session_id}')
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/apps/<app_name>/users/<user_id>/sessions/<session_id>', methods=['POST'])
def create_session_with_id(app_name, user_id, session_id):
    """Proxy to ADK create session with ID endpoint"""
    try:
        response = adk_client.request(
            'POST',
            f'/apps/{app_name}/users/{user_id}/sessions/{session_id}',
            json=request.json
        )
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/apps/<app_name>/users/<user_id>/sessions/<session_id>', methods=['DELETE'])
def delete_session(app_name, user_id, session_id):
    """Proxy to ADK delete session endpoint"""
    try:
        response = adk_client.request('DELETE', f'/apps/{app_name}/users/{user_id}/sessions/{session_id}')
        return jsonify({}), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/run', methods=['POST'])
def agent_run():
    """Proxy to ADK run endpoint with session creation"""
    try:
        request_data = request.json
        app_name = request_data.get('appName', 'oracle_agent')
        user_id = request_data.get('userId')
        session_id = request_data.get('sessionId')
        
        if not user_id or not session_id:
            return jsonify({'error': 'userId and sessionId are required'}), 400
        
        # Ensure session exists before running
        ensure_adk_session(app_name, user_id, session_id)
        
        # Now run the agent
        response = adk_client.request('POST', '/run', json=request_data)
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 503


@app.route('/run_sse', methods=['POST'])
def agent_run_sse():
    """Proxy to ADK run endpoint (non-streaming) with session creation"""
    try:
        request_data = request.json
        app_name = request_data.get('appName', 'oracle_agent')
        user_id = request_data.get('userId')
        session_id = request_data.get('sessionId')
        
        if not user_id or not session_id:
            return jsonify({'error': 'userId and sessionId are required'}), 400
        
        # Ensure session exists before running
        ensure_adk_session(app_name, user_id, session_id)
        
        # Set streaming to false and call /run endpoint
        request_data['streaming'] = False
        response = adk_client.request('POST', '/run', json=request_data)
        return response.json(), response.status_code
        
    except Exception as e:
        return jsonify({'error': str(e)}), 503


# ===== Web UI Endpoints =====

@app.route('/')
def index():
    """Main chat interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    if 'created_at' not in session:
        session['created_at'] = datetime.now().isoformat()
    
    session_id = session['session_id']
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            'created_at': session['created_at'],
            'messages': [],
            'context': {},
            'user_id': session['user_id']
        }
    
    # Get available agents from ADK
    available_agents = []
    selected_agent = request.args.get('agent', 'oracle_agent')  # Default to oracle_agent
    
    try:
        apps_response = adk_client.request('GET', '/list-apps')
        apps = apps_response.json()
        
        # Map app names to user-friendly info
        agent_mapping = {
            'oracle_agent': {
                'name': 'Oracle Financial Agent',
                'description': 'AI-powered financial assistant with future predictions',
                'icon': 'fa-crystal-ball',
                'type': 'financial'
            },
            'tax_advisor_agent': {
                'name': 'Tax Advisor Agent', 
                'description': 'Professional AI-powered Tax Planning and Optimization System',
                'icon': 'fa-calculator',
                'type': 'tax'
            }
        }
        
        for app in apps:
            if app in agent_mapping:
                available_agents.append({
                    'id': app,
                    **agent_mapping[app],
                    'available': True
                })
        
        # Set current agent info
        current_agent = next((agent for agent in available_agents if agent['id'] == selected_agent), 
                           available_agents[0] if available_agents else None)
        
        agent_info = {
            'loaded': True,
            'current': current_agent,
            'available': available_agents,
            'apps': apps
        }
        
    except Exception as e:
        logger.error(f"Error fetching apps: {e}")
        # Fallback agent info
        agent_info = {
            'loaded': False,
            'current': {
                'id': selected_agent,
                'name': 'Oracle Agent',
                'description': 'AI-powered financial assistant',
                'icon': 'fa-crystal-ball',
                'type': 'financial'
            },
            'available': [],
            'apps': []
        }
    
    return render_template('index.html', 
                         session_id=session_id,
                         agent_info=agent_info,
                         selected_agent=selected_agent,
                         current_time=datetime.now(),
                         adk_url=ADK_BASE_URL)


@app.route('/health')
def health_check():
    """Health check endpoint"""
    # Check Google Cloud authentication
    try:
        from google.auth import default
        credentials, project = default()
        auth_status = {'authenticated': True, 'project': project}
    except Exception as e:
        auth_status = {'authenticated': False, 'error': str(e)}
    
    # Check ADK connection
    adk_status = {'connected': False}
    try:
        response = adk_client.request('GET', '/health')
        adk_status = {
            'connected': True, 
            'status_code': response.status_code,
            'url': ADK_BASE_URL
        }
    except:
        adk_status['url'] = ADK_BASE_URL
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'adk_connection': adk_status,
        'active_sessions': len(active_sessions),
        'google_cloud_auth': auth_status
    })


@app.route('/api/chat', methods=['POST'])
def chat_api():
    """REST API endpoint for chat - uses ADK /run endpoint with proper session flow"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', session.get('session_id'))
        app_name = data.get('app_name', 'oracle_agent')  # Support dynamic agent selection
        
        # Get user_id
        user_id = None
        if session_id in active_sessions:
            user_id = active_sessions[session_id].get('user_id')
        if not user_id:
            user_id = session.get('user_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Empty message'
            }), 400
        
        # Ensure session exists in ADK before running
        ensure_adk_session(app_name, user_id, session_id)
        
        # Call ADK /run endpoint
        adk_request = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "parts": [{"text": user_message}],
                "role": "user"
            },
            "streaming": False
        }
        
        response = adk_client.request('POST', '/run', json=adk_request)
        events = response.json()
        
        # Extract response text from events
        response_text = ""
        metadata = {}
        
        logger.info(f"Processing {len(events)} events from ADK")
        
        for event in events:
            logger.info(f"Event: {json.dumps(event, indent=2)}")
            
            if event.get('content', {}).get('parts'):
                for part in event['content']['parts']:
                    if part.get('text'):
                        response_text += part['text']
                    elif part.get('functionCall'):
                        metadata.setdefault('function_calls', []).append(part['functionCall'])
            
            if event.get('usageMetadata'):
                metadata['usage'] = event['usageMetadata']
        
        # Update local session
        if session_id in active_sessions:
            active_sessions[session_id]['messages'].extend([
                {
                    'role': 'user',
                    'content': user_message,
                    'timestamp': datetime.now().isoformat(),
                    'agent': app_name
                },
                {
                    'role': 'assistant',
                    'content': response_text.strip(),
                    'timestamp': datetime.now().isoformat(),
                    'agent': app_name
                }
            ])
        
        return jsonify({
            'success': True,
            'response': response_text.strip(),
            'metadata': metadata,
            'session_id': session_id,
            'agent': app_name,
            'events': events  # Include raw events for debugging
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get list of available agents"""
    try:
        apps_response = adk_client.request('GET', '/list-apps')
        apps = apps_response.json()
        
        # Map app names to user-friendly info
        agent_mapping = {
            'oracle_agent': {
                'name': 'Oracle Financial Agent',
                'description': 'AI-powered financial assistant with future predictions',
                'icon': 'fa-crystal-ball',
                'type': 'financial',
                'capabilities': [
                    'Financial Future Simulations',
                    'Temporal Analysis', 
                    'Decision Impact Prophecies',
                    'Wealth Timeline Predictions'
                ]
            },
            'tax_advisor_agent': {
                'name': 'Tax Advisor Agent',
                'description': 'Professional AI-powered Tax Planning and Optimization System',
                'icon': 'fa-calculator',
                'type': 'tax',
                'capabilities': [
                    'Tax Regime Analysis',
                    'Deduction Optimization',
                    'Tax Planning Strategies',
                    'Scenario Modeling'
                ]
            }
        }
        
        available_agents = []
        for app in apps:
            if app in agent_mapping:
                available_agents.append({
                    'id': app,
                    **agent_mapping[app],
                    'available': True
                })
        
        return jsonify({
            'success': True,
            'agents': available_agents
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 503


@app.route('/api/switch-agent', methods=['POST'])
def switch_agent():
    """Switch to a different agent"""
    try:
        data = request.json
        agent_id = data.get('agent_id')
        
        if not agent_id:
            return jsonify({
                'success': False,
                'error': 'Agent ID required'
            }), 400
        
        # Verify agent exists
        apps_response = adk_client.request('GET', '/list-apps')
        apps = apps_response.json()
        
        if agent_id not in apps:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
        
        # Create new session for the agent
        new_session_id = str(uuid.uuid4())
        user_id = session.get('user_id', str(uuid.uuid4()))
        
        # Store new session
        active_sessions[new_session_id] = {
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'context': {},
            'user_id': user_id,
            'agent_id': agent_id
        }
        
        session['session_id'] = new_session_id
        
        return jsonify({
            'success': True,
            'session_id': new_session_id,
            'agent_id': agent_id,
            'redirect_url': f'/?agent={agent_id}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    """Check Google Cloud authentication status"""
    try:
        from google.auth import default
        credentials, project = default()
        return jsonify({
            'authenticated': True,
            'project': project,
            'method': 'Application Default Credentials'
        })
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'error': str(e),
            'instructions': 'Run: gcloud auth application-default login'
        }), 401


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'status': 'Connected to server'})


@socketio.on('join_session')
def handle_join_session(data):
    """Handle client joining a session room"""
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        logger.info(f"Client {request.sid} joined session {session_id}")
        emit('joined', {'session_id': session_id})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle incoming chat message via WebSocket using /run endpoint (non-streaming)"""
    try:
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()
        app_name = data.get('app_name', 'oracle_agent')  # Support dynamic agent selection
        
        if not session_id or not user_message:
            emit('error', {'error': 'Invalid message or session'})
            return
        
        # Get user_id
        user_id = 'default'
        if session_id in active_sessions:
            user_id = active_sessions[session_id].get('user_id', 'default')
            # Update agent in session if provided
            if app_name:
                active_sessions[session_id]['agent_id'] = app_name
        
        # Ensure session exists in ADK before running
        ensure_adk_session(app_name, user_id, session_id)
        
        # Emit typing indicator
        emit('agent_typing', {'typing': True})
        
        # Store user message
        if session_id in active_sessions:
            active_sessions[session_id]['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat(),
                'agent': app_name
            })
        
        # Call ADK /run endpoint (non-streaming)
        adk_request = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "parts": [{"text": user_message}],
                "role": "user"
            },
            "streaming": False
        }
        
        response = adk_client.request('POST', '/run', json=adk_request)
        events = response.json()
        
        # Extract response text from events
        full_response = ""
        
        logger.info(f"Processing {len(events)} events from ADK")
        
        for event in events:
            logger.info(f"Event content: {event.get('content', {})}")
            
            if event.get('content', {}).get('parts'):
                for part in event['content']['parts']:
                    if part.get('text'):
                        full_response += part['text']
                        logger.info(f"Added text: {part['text'][:100]}...")  # Log first 100 chars
        
        logger.info(f"Final response length: {len(full_response)}")
        logger.info(f"Full response: {full_response}")
        
        # Store complete response
        if session_id in active_sessions and full_response:
            active_sessions[session_id]['messages'].append({
                'role': 'assistant',
                'content': full_response,
                'timestamp': datetime.now().isoformat(),
                'agent': app_name
            })
        
        # Send complete response to the specific client
        emit('agent_response', {
            'response': full_response,
            'timestamp': datetime.now().isoformat(),
            'agent': app_name
        })
        
        # Stop typing indicator
        emit('agent_typing', {'typing': False})
        
    except Exception as e:
        logger.error(f"WebSocket chat error: {str(e)}", exc_info=True)
        emit('agent_error', {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })
        emit('agent_typing', {'typing': False})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask ADK Proxy Server on port {port}")
    logger.info(f"ADK Server URL: {ADK_BASE_URL}")
    logger.info(f"Debug mode: {debug}")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        use_reloader=debug
    )