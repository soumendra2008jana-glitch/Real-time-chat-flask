from gevent import monkey

monkey.patch_all()

import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "chat-fallback-secret-key"
)

# Allow all origins so your deployed app can connect properly
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
  return render_template("chat.html")


@socketio.on("join")
def handle_join(data):
  username = data.get("username", "Anonymous")
  room = data.get("room", "general")
  join_room(room)
  emit(
      "message",
      {"user": "System", "msg": f"{username} has joined the room."},
      to=room,
  )


@socketio.on("send_message")
def handle_message(data):
  room = data.get("room", "general")
  emit(
      "message",
      {
          "user": data.get("username", "Anonymous"),
          "msg": data.get("msg", ""),
          "timestamp": data.get("timestamp"),
      },
      to=room,
  )


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  socketio.run(app, host="0.0.0.0", port=port)