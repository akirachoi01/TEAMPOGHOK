from flask import Flask, render_template, request  # ← Dagdagan ito!
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}  # Dictionary to store connected users

@app.route("/")
def index():
    return render_template("index.html")
# Gamitin ang tamang PORT
PORT = int(os.getenv("PORT", 8000))

@socketio.on("connect")
def handle_connect():
    print("A user connected")

@socketio.on("disconnect")
def handle_disconnect():
    for username, sid in users.items():
        if sid == request.sid:  # ← Dapat may `request`
            del users[username]
            break
    emit("update_users", list(users.keys()), broadcast=True)

@socketio.on("set_username")
def set_username(username):
    users[username] = request.sid  # ← Dapat may `request`
    emit("update_users", list(users.keys()), broadcast=True)

@socketio.on("message")
def handle_message(data):
    sender = data["sender"]
    message = data["message"]
    send(f"{sender}: {message}", broadcast=True)

@socketio.on("private_message")
def handle_private_message(data):
    recipient = data["recipient"]
    sender = data["sender"]
    message = data["message"]
    
    if recipient in users:
        recipient_sid = users[recipient]
        emit("private_message", {"sender": sender, "message": message}, room=recipient_sid)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
