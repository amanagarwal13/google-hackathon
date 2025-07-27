#!/usr/bin/env python
"""
Run script for Flask ADK Agent Server
Provides easy startup with environment detection and optional ADK web launch
"""

import os
import sys
import subprocess
import platform
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
        return True
    except ImportError:
        print("⚠️  Google ADK not found. Make sure to install it for agent support")
        return False

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

def launch_adk_web():
    """Launch ADK web in a new terminal"""
    try:
        agent_path = os.environ.get('AGENT_PATH', './agents/oracle_agent')
        
        # Get the absolute path to the agent
        abs_agent_path = os.path.abspath(agent_path)
        
        # Determine the command based on the operating system
        system = platform.system().lower()
        
        if system == "windows":
            # Windows - use start command to open new Command Prompt
            cmd = f'start cmd /k "cd /d "{abs_agent_path}" && adk web"'
            subprocess.Popen(cmd, shell=True)
        elif system == "darwin":  # macOS
            # macOS - use AppleScript to open new Terminal
            script = f'''
            tell application "Terminal"
                do script "cd '{abs_agent_path}' && adk web"
                activate
            end tell
            '''
            subprocess.Popen(['osascript', '-e', script])
        else:  # Linux and others
            # Try different terminal emulators
            terminals = ['gnome-terminal', 'xterm', 'konsole', 'xfce4-terminal']
            for terminal in terminals:
                try:
                    if terminal == 'gnome-terminal':
                        subprocess.Popen([terminal, '--', 'bash', '-c', f'cd "{abs_agent_path}" && adk web; exec bash'])
                    else:
                        subprocess.Popen([terminal, '-e', f'bash -c "cd \\"{abs_agent_path}\\" && adk web; exec bash"'])
                    break
                except FileNotFoundError:
                    continue
            else:
                print("⚠️  Could not find a terminal emulator. Please manually run: adk web")
                return False
        
        print(f"🚀 Launching ADK web in new terminal from: {abs_agent_path}")
        print(f"   ADK Web URL: http://localhost:8000")
        return True
        
    except Exception as e:
        print(f"❌ Failed to launch ADK web: {e}")
        print("   You can manually run: adk web")
        return False

def main():
    """Main run function"""
    print("🚀 Starting Flask ADK Agent Server")
    print("-" * 40)
    
    # Parse command line arguments
    launch_adk = '--with-adk' in sys.argv or '--adk' in sys.argv
    flask_only = '--flask-only' in sys.argv
    
    # Load environment
    load_env()
    
    # Check dependencies
    adk_available = check_dependencies()
    
    # Check Google Cloud authentication (same as Oracle Agent)
    auth_ok = check_google_cloud_auth()
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    # Check agent
    agent_ok = check_agent()
    
    # Launch ADK web if requested and available
    adk_launched = False
    if launch_adk and adk_available and agent_ok:
        print(f"\n🌐 Launching ADK Web Interface...")
        adk_launched = launch_adk_web()
        if adk_launched:
            print("   ✅ ADK web launched in separate terminal")
            print("   🔗 ADK Web: http://localhost:8000")
        else:
            print("   ❌ Failed to launch ADK web automatically")
    elif launch_adk and not adk_available:
        print("\n⚠️  ADK not available - skipping ADK web launch")
    elif launch_adk and not agent_ok:
        print("\n⚠️  Agent not found - skipping ADK web launch")
    
    # Summary
    print("\n" + "=" * 40)
    print("STARTUP SUMMARY")
    print("=" * 40)
    
    if auth_ok and env_ok and agent_ok:
        print("✅ All checks passed - ready to start Flask server!")
    else:
        print("⚠️  Some issues detected:")
        if not auth_ok:
            print("   - Google Cloud authentication needed")
        if not env_ok:
            print("   - Environment variables missing")
        if not agent_ok:
            print("   - Agent not found")
        print("\nThe Flask server will start, but some features may not work.")
    
    if adk_launched:
        print("🌐 ADK Web: http://localhost:8000 (native ADK interface)")
    
    # Determine environment
    flask_env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n📌 Environment: {flask_env}")
    print(f"📌 Flask Port: {port}")
    print(f"📌 Authentication: {'✅ Ready' if auth_ok else '❌ Not configured'}")
    
    if adk_launched:
        print(f"\n🎯 Available Interfaces:")
        print(f"   🔮 ADK Web (Native):  http://localhost:8000")
        print(f"   🌐 Flask Chat:        http://localhost:{port}")
        print(f"   📊 Flask Health:      http://localhost:{port}/health")
    
    if flask_env == 'production':
        print("\n🏭 Starting Flask server in PRODUCTION mode")
        
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
        print("\n🔧 Starting Flask server in DEVELOPMENT mode")
        print(f"🌐 Flask Chat Interface: http://localhost:{port}")
        print(f"🔍 Health Check: http://localhost:{port}/health")
        print(f"🔐 Auth Status: http://localhost:{port}/api/auth/status")
        
        if adk_launched:
            print(f"\n💡 Use both interfaces:")
            print(f"   - ADK Web for native agent interaction")
            print(f"   - Flask Chat for conversational UI with same agent")
        
        from app import app, socketio
        socketio.run(app, host='0.0.0.0', port=port, debug=True, use_reloader=True)

def print_usage():
    """Print usage information"""
    print("""
Flask ADK Agent Server - Usage Options:

Basic Usage:
    python run.py                    # Start Flask server only
    python run.py --with-adk         # Start Flask + ADK web in separate terminals
    python run.py --adk              # Same as --with-adk (short form)
    python run.py --flask-only       # Explicitly start Flask only
    
Environment:
    FLASK_ENV=development            # Development mode (default)
    FLASK_ENV=production             # Production mode
    PORT=5000                        # Flask server port (default: 5000)
    AGENT_PATH=./agents/oracle_agent # Path to your ADK agent
    
Examples:
    # Development with both interfaces
    python run.py --with-adk
    # → ADK Web: http://localhost:8000
    # → Flask Chat: http://localhost:5000
    
    # Production Flask only
    FLASK_ENV=production python run.py
    
    # Custom port with ADK
    PORT=8080 python run.py --adk
    """)

if __name__ == '__main__':
    if '--help' in sys.argv or '-h' in sys.argv:
        print_usage()
        sys.exit(0)
        
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down servers...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1) 