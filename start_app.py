import subprocess
import webbrowser
import time
import sys

def start_services():
    print("🚀 Starting ResQAlert Services...")
    
    # Start Flask authentication server
    print("📡 Starting authentication server on http://localhost:5000")
    flask_process = subprocess.Popen([sys.executable, 'auth_server.py'])
    
    # Wait for Flask to start
    time.sleep(3)
    
    # Open INDEX page in browser (landing page)
    print("🌐 Opening ResQAlert homepage...")
    webbrowser.open('http://localhost:5000')
    
    print("\n✅ All services started!")
    print("📋 Homepage: http://localhost:5000")
    print("🔐 Login: http://localhost:5000/login.html")
    print("📊 Streamlit will launch after successful login")
    print("\n⚠️  Press Ctrl+C to stop all services\n")
    
    try:
        flask_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        flask_process.terminate()
        flask_process.wait()
        print("✅ All services stopped")

if __name__ == '__main__':
    start_services()
