"""
Flask Server for ADK Agent Deployment
Provides a conversational interface similar to ADK's web interface
"""

from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import uuid
import os
import logging
from datetime import datetime
import json
from typing import Dict, Any, Optional

from agent_manager import AgentManager
from config import Config, setup_google_cloud_auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup Google Cloud authentication (same as Oracle Agent)
setup_google_cloud_auth()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for API endpoints
CORS(app, resources={r"/api/*": {"origins": Config.ALLOWED_ORIGINS}})

# Initialize SocketIO with event logger
socketio = SocketIO(
    app, 
    cors_allowed_origins=Config.ALLOWED_ORIGINS,
    logger=True,
    engineio_logger=True,
    async_mode='threading'
)

# Initialize Agent Manager
agent_manager = AgentManager()

# Session store (in production, use Redis or similar)
active_sessions = {}


@app.route('/')
def index():
    """Main chat interface"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['created_at'] = datetime.now().isoformat()
    
    # Initialize session data
    session_id = session['session_id']
    if session_id not in active_sessions:
        active_sessions[session_id] = {
            'created_at': session['created_at'],
            'messages': [],
            'context': {},
            'agent_state': None
        }
    
    return render_template('index.html', 
                         session_id=session_id,
                         agent_info=agent_manager.get_agent_info(),
                         current_time=datetime.now())


@app.route('/health')
def health_check():
    """Health check endpoint"""
    # Check Google Cloud authentication status
    try:
        from google.auth import default
        credentials, project = default()
        auth_status = {'authenticated': True, 'project': project}
    except Exception as e:
        auth_status = {'authenticated': False, 'error': str(e)}
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'agent_loaded': agent_manager.is_agent_loaded(),
        'active_sessions': len(active_sessions),
        'google_cloud_auth': auth_status
    })


@app.route('/api/chat', methods=['POST'])
def chat_api():
    """REST API endpoint for chat - fallback for WebSocket"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', session.get('session_id'))
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Empty message'
            }), 400
        
        # Process message
        result = agent_manager.process_message(
            message=user_message,
            session_id=session_id,
            session_data=active_sessions.get(session_id, {})
        )
        
        # Update session
        if session_id in active_sessions:
            active_sessions[session_id]['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            active_sessions[session_id]['messages'].append({
                'role': 'assistant',
                'content': result['response'],
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'response': result['response'],
            'metadata': result.get('metadata', {}),
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session history"""
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session_id,
        'messages': active_sessions[session_id]['messages'],
        'created_at': active_sessions[session_id]['created_at']
    })


@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Clear session history"""
    if session_id in active_sessions:
        active_sessions[session_id]['messages'] = []
        active_sessions[session_id]['context'] = {}
        active_sessions[session_id]['agent_state'] = None
    
    return jsonify({'success': True})


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


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('join_session')
def handle_join_session(data):
    """Join user to their session room"""
    session_id = data.get('session_id')
    if not session_id:
        emit('error', {'error': 'No session ID provided'})
        return
    
    join_room(session_id)
    
    # Send session history if exists
    if session_id in active_sessions:
        emit('session_history', {
            'messages': active_sessions[session_id]['messages']
        })
    
    emit('joined', {
        'session_id': session_id,
        'message': f'Joined session {session_id}'
    })
    
    logger.info(f"Client {request.sid} joined session {session_id}")


@socketio.on('leave_session')
def handle_leave_session(data):
    """Leave session room"""
    session_id = data.get('session_id')
    if session_id:
        leave_room(session_id)
        emit('left', {'session_id': session_id})


@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle incoming chat message via WebSocket"""
    try:
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()
        
        if not session_id or not user_message:
            emit('error', {'error': 'Invalid message or session'})
            return
        
        # Emit typing indicator to room
        socketio.emit('agent_typing', {'typing': True}, room=session_id)
        
        # Store user message
        if session_id in active_sessions:
            active_sessions[session_id]['messages'].append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
        
        # Process message with agent
        result = agent_manager.process_message(
            message=user_message,
            session_id=session_id,
            session_data=active_sessions.get(session_id, {})
        )
        
        # Store agent response
        if session_id in active_sessions:
            active_sessions[session_id]['messages'].append({
                'role': 'assistant',
                'content': result['response'],
                'timestamp': datetime.now().isoformat(),
                'metadata': result.get('metadata', {})
            })
        
        # Send response to room
        socketio.emit('agent_response', {
            'response': result['response'],
            'metadata': result.get('metadata', {}),
            'timestamp': datetime.now().isoformat()
        }, room=session_id)
        
        # Stop typing indicator
        socketio.emit('agent_typing', {'typing': False}, room=session_id)
        
    except Exception as e:
        logger.error(f"WebSocket chat error: {str(e)}", exc_info=True)
        socketio.emit('agent_error', {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, room=session_id)
        socketio.emit('agent_typing', {'typing': False}, room=session_id)


@socketio.on('get_agent_info')
def handle_get_agent_info():
    """Get information about loaded agent"""
    emit('agent_info', agent_manager.get_agent_info())


@socketio.on('ping')
def handle_ping():
    """Handle ping for connection keep-alive"""
    emit('pong', {'timestamp': datetime.now().isoformat()})


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500


# Cleanup function
def cleanup_old_sessions():
    """Clean up old sessions (run periodically)"""
    cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours
    sessions_to_remove = []
    
    for session_id, session_data in active_sessions.items():
        created_at = datetime.fromisoformat(session_data['created_at']).timestamp()
        if created_at < cutoff_time:
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        del active_sessions[session_id]
        logger.info(f"Cleaned up old session: {session_id}")


if __name__ == '__main__':
    # Run the Flask app with SocketIO
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Flask ADK Agent Server on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Agent loaded: {agent_manager.is_agent_loaded()}")
    
    socketio.run(
        app, 
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        use_reloader=debug
    ) 