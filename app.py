from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import sqlite3
import threading
import time

DB_PATH = "./data.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# ----------------- DATABASE -----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def broadcast_map_data():
    """Continuously send map data to clients via WebSocket."""
    while True:
        db = get_db()
        rows = db.execute(
            "SELECT source, location, timestamp, message FROM messages ORDER BY id DESC LIMIT 200"
        ).fetchall()
        data = []
        for r in rows:
            try:
                lat, lon = r["location"].split(",")
                data.append({
                    "source": r["source"],
                    "lat": float(lat),
                    "lon": float(lon),
                    "timestamp": r["timestamp"],
                    "message": r["message"]
                })
            except Exception:
                continue
        socketio.emit("map_update", data)
        time.sleep(5)  # send updates every 5s

# ----------------- ROUTES -----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/devices")
def api_devices():
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page
    db = get_db()
    rows = db.execute(
        "SELECT * FROM devices ORDER BY last_seen DESC LIMIT ? OFFSET ?",
        (per_page, offset)
    ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/messages")
def api_messages():
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page
    db = get_db()
    rows = db.execute(
        "SELECT * FROM messages ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset)
    ).fetchall()
    return jsonify([dict(r) for r in rows])

# ----------------- THREAD -----------------
threading.Thread(target=broadcast_map_data, daemon=True).start()

# ----------------- RUN -----------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)

