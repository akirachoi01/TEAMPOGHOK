import os
from flask import Flask
from flask_socketio import SocketIO
from flask import Flask, render_template, request, session  # ← Dagdagan ito!
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_session import Session

from flask_session import Session  # ← Import Flask-Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["SESSION_TYPE"] = "filesystem"  # Para sa session storage

Session(app)  # Initialize session management
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}  # Dictionary para sa mga user

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    print("A user connected")

@socketio.on("disconnect")
def handle_disconnect():
    username = session.get("username")  # Kunin ang username mula sa session
    if username and username in users:
        del users[username]
    session.clear()  # Linisin ang session
    emit("update_users", list(users.keys()), broadcast=True)

@socketio.on("set_username")
def set_username(username):
    session["username"] = username  # I-save ang username sa session
    users[username] = request.sid
    emit("update_users", list(users.keys()), broadcast=True)

@socketio.on("message")
def handle_message(data):
    sender = session.get("username", "Anonymous")  # Kunin mula session
    message = data["message"]
    send(f"{sender}: {message}", broadcast=True)

@socketio.on("private_message")
def handle_private_message(data):
    recipient = data["recipient"]
    sender = session.get("username", "Anonymous")  # Kunin mula session
    message = data["message"]

    if recipient in users:
        recipient_sid = users[recipient]
        emit("private_message", {"sender": sender, "message": message}, room=recipient_sid)

# Gamitin ang tamang PORT
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=PORT, debug=False, allow_unsafe_werkzeug=True)
