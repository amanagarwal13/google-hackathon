#!/usr/bin/env python
"""
Run script for Flask ADK Agent Server
Provides easy startup with environment detection
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import flask_socketio
        print("✅ Core dependencies found")
    except ImportError:
        print("❌ Missing dependencies. Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Check for ADK
    try:
        import google.adk
        print("✅ Google ADK found")
    except ImportError:
        print("⚠️  Google ADK not found. Make sure to install it for agent support")

def check_google_cloud_auth():
    """Check Google Cloud authentication (same as Oracle Agent)"""
    try:
        from google.auth import default
        credentials, project = default()
        print(f"✅ Google Cloud authentication successful")
        print(f"   Project: {project}")
        print(f"   Method: Application Default Credentials")
        return True
    except Exception as e:
        print("❌ Google Cloud authentication not configured")
        print(f"   Error: {e}")
        print("\n🔧 To fix this, run the following commands (same as Oracle Agent):")
        print("   gcloud auth application-default login")
        print("   gcloud auth application-default set-quota-project YOUR_PROJECT_ID")
        return False

def check_environment_variables():
    """Check required environment variables"""
    required_vars = {
        'GOOGLE_CLOUD_PROJECT': 'Google Cloud project ID',
        'GOOGLE_GENAI_USE_VERTEXAI': 'Use Vertex AI for Gemini (should be true)'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Not set ({description})")
            missing_vars.append(var)
    
    optional_vars = {
        'GOOGLE_CLOUD_LOCATION': 'us-central1',
        'GOOGLE_CLOUD_STORAGE_BUCKET': 'Your storage bucket'
    }
    
    for var, default in optional_vars.items():
        value = os.environ.get(var, default)
        print(f"📌 {var}: {value}")
    
    return len(missing_vars) == 0

def check_agent():
    """Check if agent is available"""
    agent_path = os.environ.get('AGENT_PATH', './agents/oracle_agent')
    if os.path.exists(agent_path):
        print(f"✅ Agent found at: {agent_path}")
        
        # Check if it's an Oracle agent specifically
        if 'oracle_agent' in agent_path:
            print("   🔮 Oracle Agent detected - Fi MCP integration available")
        
        return True
    else:
        print(f"⚠️  Agent not found at: {agent_path}")
        print("   Copy your agent to the agents/ directory or update AGENT_PATH")
        return False

def load_env():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        print("✅ Loading .env file")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    else:
        print("⚠️  No .env file found. Using system environment variables")
        print("   Create .env file with your configuration")

def main():
    """Main run function"""
    print("🚀 Starting Flask ADK Agent Server")
    print("-" * 40)
    
    # Load environment
    load_env()
    
    # Check dependencies
    check_dependencies()
    
    # Check Google Cloud authentication (same as Oracle Agent)
    auth_ok = check_google_cloud_auth()
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Check agent
    agent_ok = check_agent()
    
    # Summary
    print("\n" + "=" * 40)
    print("STARTUP SUMMARY")
    print("=" * 40)
    
    if auth_ok and env_ok and agent_ok:
        print("✅ All checks passed - ready to start!")
    else:
        print("⚠️  Some issues detected:")
        if not auth_ok:
            print("   - Google Cloud authentication needed")
        if not env_ok:
            print("   - Environment variables missing")
        if not agent_ok:
            print("   - Agent not found")
        print("\nThe server will start, but some features may not work.")
    
    # Determine environment
    flask_env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n📌 Environment: {flask_env}")
    print(f"📌 Port: {port}")
    print(f"📌 Authentication: {'✅ Ready' if auth_ok else '❌ Not configured'}")
    
    if flask_env == 'production':
        print("\n🏭 Starting in PRODUCTION mode")
        
        # Check for production server
        try:
            import eventlet
            import gunicorn
            print("✅ Using Gunicorn with eventlet")
            cmd = [
                'gunicorn',
                '-k', 'eventlet',
                '-w', '1',
                '--bind', f'0.0.0.0:{port}',
                '--timeout', '300',
                '--log-level', 'info',
                'app:app'
            ]
            subprocess.run(cmd)
        except ImportError:
            try:
                import waitress
                print("✅ Using Waitress (Windows compatible)")
                from app import app
                waitress.serve(app, host='0.0.0.0', port=port)
            except ImportError:
                print("⚠️  No production server found. Using Flask development server")
                print("   Install gunicorn or waitress for production")
                from app import app, socketio
                socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        print("\n🔧 Starting in DEVELOPMENT mode")
        print(f"🌐 Open: http://localhost:{port}")
        print(f"🔍 Health check: http://localhost:{port}/health")
        print(f"🔐 Auth status: http://localhost:{port}/api/auth/status")
        
        from app import app, socketio
        socketio.run(app, host='0.0.0.0', port=port, debug=True, use_reloader=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1) 