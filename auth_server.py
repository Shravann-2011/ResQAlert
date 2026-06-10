from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import subprocess
import os

app = Flask(__name__, static_folder='static')
CORS(app)

DB_PATH = "database/users.db"
ACTIVE_SESSIONS = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Serve static HTML files
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, name FROM users WHERE email = ? AND password = ?", 
                   (email, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session_token = secrets.token_hex(16)
        ACTIVE_SESSIONS[session_token] = {
            'user_id': user[0],
            'email': user[1],
            'name': user[2]
        }
        
        # Start Streamlit app
        streamlit_url = start_streamlit()
        
        return jsonify({
            'success': True,
            'token': session_token,
            'user': {'id': user[0], 'email': user[1], 'name': user[2]},
            'redirect_url': streamlit_url
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Insert new user
    cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                   (name, email, hash_password(password)))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    session_token = secrets.token_hex(16)
    ACTIVE_SESSIONS[session_token] = {
        'user_id': user_id,
        'email': email,
        'name': name
    }
    
    # Start Streamlit app
    streamlit_url = start_streamlit()
    
    return jsonify({
        'success': True,
        'token': session_token,
        'user': {'id': user_id, 'email': email, 'name': name},
        'redirect_url': streamlit_url
    })

@app.route('/api/verify-session', methods=['GET'])
def verify_session():
    token = request.headers.get('Authorization')
    if token in ACTIVE_SESSIONS:
        return jsonify({'success': True, 'user': ACTIVE_SESSIONS[token]})
    return jsonify({'success': False}), 401

def start_streamlit():
    """Start Streamlit app if not already running"""
    try:
        # Check if streamlit is already running
        import requests
        try:
            requests.get('http://localhost:8501', timeout=1)
            return 'http://localhost:8501'
        except:
            # Start Streamlit in background
            subprocess.Popen(['streamlit', 'run', 'main.py', '--server.headless=true'])
            import time
            time.sleep(3)  # Give Streamlit time to start
            return 'http://localhost:8501'
    except Exception as e:
        print(f"Error starting Streamlit: {e}")
        return 'http://localhost:8501'

if __name__ == '__main__':
    print("🚀 Starting ResQAlert Authentication Server...")
    print("📡 Server running at: http://localhost:5000")
    print("🌐 Access the app at: http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
