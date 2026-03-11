from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store messages in memory
messages = []

@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    HTTP endpoint for Node-RED to send messages
    Node-RED should use HTTP Request node to POST here
    """
    from flask import request
    
    try:
        data = request.get_json()
        
        # Add timestamp if not present
        if 'timestamp' not in data:
            from datetime import datetime
            data['timestamp'] = datetime.now().isoformat()
        
        # Store message
        messages.append(data)
        
        # Keep only last 100 messages
        if len(messages) > 100:
            messages.pop(0)
        
        # Broadcast to all connected web clients
        socketio.emit('new_message', {'data': data})
        
        print(f"✅ Received message from Node-RED: {data}")
        
        return {'status': 'success', 'message': 'Message received'}, 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return {'status': 'error', 'message': str(e)}, 400

@socketio.on('connect')
def handle_connect():
    """Handle new client connection"""
    print('🔌 Client connected')
    # Send message history to newly connected client
    emit('message_history', {'messages': messages})
    emit('status', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('🔌 Client disconnected')

@socketio.on('clear_messages')
def handle_clear_messages():
    """Clear all messages"""
    global messages
    messages = []
    socketio.emit('messages_cleared', {})
    print('🗑️ Messages cleared')

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Flask + Socket.IO Server Starting")
    print("=" * 60)
    print("📡 Web UI: http://localhost:5001")
    print("📥 Webhook: http://localhost:5001/webhook")
    print("=" * 60)
    print("\n🔧 Node-RED Configuration:")
    print("   1. Add HTTP Request node")
    print("   2. Set Method: POST")
    print("   3. Set URL: http://localhost:5001/webhook")
    print("   4. Set payload to msg.payload")
    print("=" * 60)
    
    socketio.run(app, debug=True, host='127.0.0.1', port=5001, allow_unsafe_werkzeug=True)

# Made with Bob
