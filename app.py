from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")

socketio = SocketIO(app, cors_allowed_origins="*")

# Store messages in memory
messages = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return {"status": "ok"}, 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data:
            return {"status": "error", "message": "No JSON body received"}, 400

        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()

        messages.append(data)

        if len(messages) > 100:
            messages.pop(0)

        socketio.emit("new_message", {"data": data})

        print(f"Received message: {data}")
        return {"status": "success", "message": "Message received"}, 200

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}, 400

@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("message_history", {"messages": messages})
    emit("status", {"data": "Connected to server"})

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("clear_messages")
def handle_clear_messages():
    global messages
    messages = []
    socketio.emit("messages_cleared", {})
    print("Messages cleared")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
