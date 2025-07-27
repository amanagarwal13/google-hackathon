#!/usr/bin/env python
"""
Demo script showing dual interface capabilities
"""

import time
import webbrowser
import subprocess
import sys
from pathlib import Path

def demo_dual_interfaces():
    """Demonstrate running both ADK web and Flask interfaces"""
    
    print("🎯 Flask ADK Agent Server - Dual Interface Demo")
    print("=" * 50)
    
    print("\nThis demo shows how to run both interfaces simultaneously:")
    print("🔮 ADK Web (Native):  http://localhost:8000")
    print("🌐 Flask Chat:        http://localhost:5000")
    
    print("\n📋 Prerequisites:")
    print("1. Agent configured in AGENT_PATH")
    print("2. Google Cloud authentication setup")
    print("3. All dependencies installed")
    
    # Check if .env exists
    env_file = Path('.env')
    if not env_file.exists():
        print("\n⚠️  No .env file found!")
        print("Create .env with:")
        print("   AGENT_PATH=../oracle_agent")
        print("   GOOGLE_CLOUD_PROJECT=your-project-id")
        return False
    
    print("\n✅ Environment file found")
    
    print("\n🚀 Starting dual interface demo...")
    print("\nRun this command:")
    print("   python run.py --with-adk")
    
    print("\n📋 What this does:")
    print("1. Launches ADK web in new terminal → http://localhost:8000")
    print("2. Starts Flask chat server → http://localhost:5000")
    print("3. Both connect to the same agent instance")
    
    print("\n💡 Usage scenarios:")
    print("🔧 Development:")
    print("   → Use ADK Web for testing agent responses")
    print("   → Use Flask Chat for UI/UX development")
    
    print("\n🎨 Production:")
    print("   → ADK Web for admin/developer access")
    print("   → Flask Chat for end-user interactions")
    
    print("\n🔄 Demo steps:")
    print("1. Ask the same question in both interfaces")
    print("2. Compare the responses (should be identical)")
    print("3. Notice different UI experiences")
    
    # Offer to run the demo
    if '--auto' in sys.argv:
        print("\n🤖 Auto-starting demo...")
        return run_demo()
    else:
        response = input("\n❓ Start the demo now? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return run_demo()
        else:
            print("💡 Run manually: python run.py --with-adk")
            return True

def run_demo():
    """Actually run the dual interface demo"""
    try:
        print("\n🚀 Launching dual interfaces...")
        
        # Run the dual interface launcher
        result = subprocess.run([
            sys.executable, 'run.py', '--with-adk'
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user")
        return True
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return False

def show_comparison():
    """Show interface comparison"""
    print("\n📊 Interface Comparison")
    print("-" * 30)
    
    comparison = [
        ("Purpose", "Development & Testing", "User-Facing"),
        ("UI Style", "Basic web form", "Modern chat interface"),
        ("Real-time", "Request/Response", "WebSocket + REST"),
        ("Sessions", "Single request", "Persistent conversations"),
        ("Mobile", "Basic", "Fully responsive"),
        ("Production", "Development focus", "Production-ready"),
        ("Best for", "Quick testing", "End-user interaction")
    ]
    
    print(f"{'Feature':<15} {'ADK Web':<20} {'Flask Chat':<25}")
    print("-" * 60)
    
    for feature, adk, flask in comparison:
        print(f"{feature:<15} {adk:<20} {flask:<25}")

def main():
    """Main demo function"""
    if '--help' in sys.argv:
        print("""
Flask ADK Agent Server - Demo

Usage:
    python demo.py           # Interactive demo
    python demo.py --auto    # Auto-start demo
    python demo.py --compare # Show interface comparison
    python demo.py --help    # This help
        """)
        return
    
    if '--compare' in sys.argv:
        show_comparison()
        return
    
    success = demo_dual_interfaces()
    
    if success:
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("1. Try both interfaces with your agent")
        print("2. Compare the user experiences")
        print("3. Choose the right interface for your use case")
    else:
        print("\n💥 Demo encountered issues")
        print("Check the troubleshooting section in README.md")

if __name__ == '__main__':
    main() 