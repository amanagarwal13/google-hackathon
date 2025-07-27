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
import threading
import time
import time

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

# Store for parallel universe data
parallel_universe_data = {
    'status': 'pending',
    'data': None,
    'error': None,
    'timestamp': None
}

# Available agents configuration
AVAILABLE_AGENTS = {
    'oracle_agent': {
        'name': 'Oracle Financial Agent',
        'description': 'AI-powered financial assistant for comprehensive analysis and predictions',
        'icon': 'fa-chart-line',
        'capabilities': [
            'Financial Analysis',
            'Future Predictions',
            'Scenario Modeling',
            'Timeline Analysis'
        ]
    },
    'tax_advisor_agent': {
        'name': 'Tax Advisor Agent',
        'description': 'Professional AI-powered Tax Advisor for comprehensive tax planning and optimization',
        'icon': 'fa-calculator',
        'capabilities': [
            'Tax Regime Analysis',
            'Deduction Optimization',
            'Tax Planning Strategies',
            'Scenario Modeling'
        ]
    }
}


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


def run_parallel_universe_analysis():
    """Run parallel universe analysis in background"""
    global parallel_universe_data
    
    try:
        logger.info("Starting parallel universe analysis...")
        parallel_universe_data['status'] = 'processing'
        
        # First check if parallel_universe_agent is available
        try:
            apps_response = adk_client.request('GET', '/list-apps')
            available_apps = apps_response.json()
            logger.info(f"Available apps: {available_apps}")
            
            if 'parallel_universe_agent' not in available_apps:
                logger.warning("parallel_universe_agent not found in available apps")
                parallel_universe_data['status'] = 'error'
                parallel_universe_data['error'] = 'Parallel universe agent not available'
                return
        except Exception as e:
            logger.error(f"Failed to list apps: {e}")
        
        # Generate unique IDs for this run
        user_id = f"parallel_user_{uuid.uuid4().hex[:8]}"
        session_id = f"parallel_session_{uuid.uuid4().hex[:8]}"
        app_name = "parallel_universe_agent"
        
        # Ensure session exists
        ensure_adk_session(app_name, user_id, session_id)
        
        # Prepare request
        adk_request = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "parts": [
                    {
                        "text": "This will utilize all available MCP data to generate the final JSON response"
                    }
                ],
                "role": "user"
            },
            "streaming": False
        }
        
        logger.info(f"Sending request to parallel universe agent: {json.dumps(adk_request, indent=2)}")
        
        # Make request
        response = adk_client.request('POST', '/run', json=adk_request)
        events = response.json()
        
        # Process events to extract the final JSON
        final_json = None
        all_text = ""
        
        logger.info(f"Processing {len(events)} events from parallel universe agent")
        
        # First, try to find the insight synthesizer agent's output
        for event in events:
            if event.get('author') == 'insight_synthesizer_agent':
                if event.get('content', {}).get('parts'):
                    for part in event['content']['parts']:
                        if part.get('text'):
                            text = part['text']
                            logger.info(f"Found insight synthesizer output, length: {len(text)}")
                            if text.strip().startswith('```json') and text.strip().endswith('```'):
                                json_str = text.strip()[7:-3]  # Remove ```json and ```
                                try:
                                    parsed_data = json.loads(json_str)
                                    if 'parallel_universe_analysis' in parsed_data:
                                        final_json = parsed_data
                                        logger.info("Successfully parsed parallel universe analysis from insight synthesizer")
                                        break
                                except json.JSONDecodeError as e:
                                    logger.error(f"JSON decode error: {e}")
        
        # If not found in insight synthesizer, check all events
        if not final_json:
            for event in events:
                if event.get('content', {}).get('parts'):
                    for part in event['content']['parts']:
                        if part.get('text'):
                            all_text += part['text']
                            text = part['text']
                            if text.strip().startswith('```json') and text.strip().endswith('```'):
                                json_str = text.strip()[7:-3]  # Remove ```json and ```
                                try:
                                    parsed_data = json.loads(json_str)
                                    if 'parallel_universe_analysis' in parsed_data:
                                        final_json = parsed_data
                                        logger.info("Found parallel universe analysis in general events")
                                except json.JSONDecodeError:
                                    pass
        
        if final_json:
            parallel_universe_data['status'] = 'completed'
            parallel_universe_data['data'] = final_json
            parallel_universe_data['timestamp'] = datetime.now().isoformat()
            logger.info("Parallel universe analysis completed successfully")
            logger.info(f"Data keys: {list(final_json.keys())}")
        else:
            logger.error("No valid parallel universe analysis data found in response")
            logger.error(f"Total text collected: {len(all_text)} characters")
            if all_text:
                logger.error(f"First 500 chars: {all_text[:500]}")
            parallel_universe_data['status'] = 'error'
            parallel_universe_data['error'] = "No valid parallel universe analysis data found in response"
            
    except Exception as e:
        logger.error(f"Parallel universe analysis failed: {str(e)}", exc_info=True)
        parallel_universe_data['status'] = 'error'
        parallel_universe_data['error'] = str(e)
        parallel_universe_data['timestamp'] = datetime.now().isoformat()


def start_background_analysis():
    """Start parallel universe analysis in a background thread"""
    thread = threading.Thread(target=run_parallel_universe_analysis)
    thread.daemon = True
    thread.start()
    logger.info("Background parallel universe analysis thread started")


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
    """Agent selection page"""
    return render_template('agent_selector.html', agents=AVAILABLE_AGENTS)


@app.route('/chat/<agent_name>')
def chat_interface(agent_name):
    """Main chat interface for specific agent"""
    if agent_name not in AVAILABLE_AGENTS:
        return "Agent not found", 404
    
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    if 'created_at' not in session:
        session['created_at'] = datetime.now().isoformat()
    
    # Create agent-specific session
    session_key = f"{agent_name}_{session['session_id']}"
    if session_key not in active_sessions:
        active_sessions[session_key] = {
            'created_at': session['created_at'],
            'messages': [],
            'context': {},
            'user_id': session['user_id'],
            'agent_name': agent_name
        }
    
    # Get agent info
    agent_info = AVAILABLE_AGENTS.get(agent_name, {})
    agent_info['loaded'] = True
    agent_info['type'] = agent_name
    
    return render_template('index.html', 
                         session_id=session['session_id'],
                         agent_info=agent_info,
                         agent_name=agent_name,
                         current_time=datetime.now(),
                         adk_url=ADK_BASE_URL)


@app.route('/timeline')
def timeline_view():
    """Timeline visualization page"""
    # Check if analysis needs to be triggered
    if parallel_universe_data['status'] == 'pending':
        logger.info("Timeline view accessed, triggering analysis if not started")
        start_background_analysis()
    return render_template('timeline.html')


@app.route('/api/parallel-universe-data')
def get_parallel_universe_data():
    """API endpoint to get parallel universe analysis data"""
    return jsonify(parallel_universe_data)


@app.route('/api/parallel-universe-status')
def get_parallel_universe_status():
    """Debug endpoint to check parallel universe analysis status"""
    status = {
        'current_status': parallel_universe_data['status'],
        'has_data': parallel_universe_data['data'] is not None,
        'last_updated': parallel_universe_data['timestamp'],
        'error': parallel_universe_data.get('error')
    }
    if parallel_universe_data['data']:
        status['data_keys'] = list(parallel_universe_data['data'].keys())
    return jsonify(status)


@app.route('/api/trigger-parallel-analysis', methods=['POST'])
def trigger_parallel_analysis():
    """Manually trigger parallel universe analysis"""
    start_background_analysis()
    return jsonify({'status': 'Analysis triggered', 'message': 'Check back in a few moments for results'})


@app.route('/api/test-adk-connection')
def test_adk_connection():
    """Test ADK connection and list available apps"""
    try:
        # Test health endpoint
        health_response = adk_client.request('GET', '/health')
        
        # List available apps
        apps_response = adk_client.request('GET', '/list-apps')
        available_apps = apps_response.json()
        
        return jsonify({
            'adk_connected': True,
            'adk_url': ADK_BASE_URL,
            'health_status': health_response.status_code,
            'available_apps': available_apps,
            'has_parallel_universe_agent': 'parallel_universe_agent' in available_apps
        })
    except Exception as e:
        return jsonify({
            'adk_connected': False,
            'adk_url': ADK_BASE_URL,
            'error': str(e)
        }), 503


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
        'google_cloud_auth': auth_status,
        'available_agents': list(AVAILABLE_AGENTS.keys()),
        'parallel_universe_status': parallel_universe_data['status']
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
        app_name = data.get('app_name', 'oracle_agent')
        
        # Get user_id from session store
        session_key = f"{app_name}_{session_id}"
        user_id = None
        if session_key in active_sessions:
            user_id = active_sessions[session_key].get('user_id')
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
        if session_key in active_sessions:
            active_sessions[session_key]['messages'].extend([
                {
                    'role': 'user',
                    'content': user_message,
                    'timestamp': datetime.now().isoformat()
                },
                {
                    'role': 'assistant',
                    'content': response_text.strip(),
                    'timestamp': datetime.now().isoformat()
                }
            ])
        
        return jsonify({
            'success': True,
            'response': response_text.strip(),
            'metadata': metadata,
            'session_id': session_id,
            'events': events  # Include raw events for debugging
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/status')
def auth_status():
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
    agent_name = data.get('agent_name', 'oracle_agent')
    if session_id:
        room_name = f"{agent_name}_{session_id}"
        join_room(room_name)
        logger.info(f"Client {request.sid} joined session {room_name}")
        emit('joined', {'session_id': session_id, 'agent_name': agent_name})


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
        app_name = data.get('app_name', 'oracle_agent')
        
        if not session_id or not user_message:
            emit('error', {'error': 'Invalid message or session'})
            return
        
        # Get user_id from session store
        session_key = f"{app_name}_{session_id}"
        user_id = 'default'
        if session_key in active_sessions:
            user_id = active_sessions[session_key].get('user_id', 'default')
        
        # Ensure session exists in ADK before running
        ensure_adk_session(app_name, user_id, session_id)
        
        # Emit typing indicator
        emit('agent_typing', {'typing': True})
        
        # Store user message
        if session_key in active_sessions:
            active_sessions[session_key]['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
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
        if session_key in active_sessions and full_response:
            active_sessions[session_key]['messages'].append({
                'role': 'assistant',
                'content': full_response,
                'timestamp': datetime.now().isoformat()
            })
        
        # Send complete response to the specific client
        emit('agent_response', {
            'response': full_response,
            'timestamp': datetime.now().isoformat()
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
    logger.info(f"Available agents: {list(AVAILABLE_AGENTS.keys())}")
    
    # Start parallel universe analysis in background after a short delay
    # Only in non-debug mode to avoid issues with reloader
    if not debug:
        def delayed_start():
            time.sleep(5)  # Wait 5 seconds for server to fully start
            logger.info("Starting delayed parallel universe analysis")
            start_background_analysis()
        
        delay_thread = threading.Thread(target=delayed_start)
        delay_thread.daemon = True
        delay_thread.start()
    else:
        logger.info("Debug mode - skipping automatic parallel universe analysis")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        use_reloader=debug
    )