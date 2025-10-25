# app.py
# LOCKED: Do not partially change this file unless you intend a full rollback.
# Run: python app.py
from flask import Flask, render_template, jsonify, request, send_from_directory
import os, json, threading, time

APP_ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(APP_ROOT, "data")
VIDEOS_DIR = os.path.join(APP_ROOT, "static", "videos")
COUNTER_FILE = os.path.join(DATA_DIR, "counter.json")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)

lock = threading.Lock()

# initialize files if missing
if not os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": 0}, f)

if not os.path.exists(CONFIG_FILE):
    # default to first mp4 in videos dir if present, else empty string
    default_vid = ""
    vids = [f for f in os.listdir(VIDEOS_DIR) if f.lower().endswith(".mp4")]
    if vids:
        default_vid = vids[0]
    with open(CONFIG_FILE, "w") as f:
        json.dump({"active_video": default_vid}, f)

app = Flask(__name__, static_folder="static", template_folder="templates")

def read_counter():
    with lock:
        with open(COUNTER_FILE, "r") as f:
            return json.load(f)

def write_counter(data):
    with lock:
        with open(COUNTER_FILE, "w") as f:
            json.dump(data, f)

def read_config():
    with lock:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

def write_config(data):
    with lock:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)

@app.route("/")
def index():
    # index will fetch other data via JS
    return render_template("index.html")

@app.route("/api/hit", methods=["POST"])
def api_hit():
    """Called on page load to increment visitor counter and return values."""
    with lock:
        cur = read_counter()
        cur["count"] = int(cur.get("count", 0)) + 1
        write_counter(cur)
    cfg = read_config()
    return jsonify({"count": cur["count"], "active_video": cfg.get("active_video","")})

@app.route("/api/count", methods=["GET"])
def api_count():
    cur = read_counter()
    return jsonify({"count": cur.get("count", 0)})

@app.route("/api/videos", methods=["GET"])
def api_videos():
    vids = sorted([f for f in os.listdir(VIDEOS_DIR) if f.lower().endswith(".mp4")])
    cfg = read_config()
    return jsonify({"videos": vids, "active_video": cfg.get("active_video","")})

@app.route("/api/set_video", methods=["POST"])
def api_set_video():
    data = request.get_json() or {}
    filename = data.get("filename","")
    # basic validation
    if not filename or ".." in filename or not filename.lower().endswith(".mp4"):
        return jsonify({"ok": False, "error": "Invalid filename"}), 400
    full = os.path.join(VIDEOS_DIR, filename)
    if not os.path.exists(full):
        return jsonify({"ok": False, "error": "File not found"}), 404
    cfg = read_config()
    cfg["active_video"] = filename
    write_config(cfg)
    return jsonify({"ok": True, "active_video": filename})

# Serve videos
@app.route("/videos/<path:filename>")
def videos(filename):
    return send_from_directory(VIDEOS_DIR, filename)

if __name__ == "__main__":
    print("=== TimmyTime LIVE — Flask dev server ===")
    print("Put your mp4 files into ./static/videos/ (e.g. clip1.mp4).")
    print("Run: python app.py  then open http://127.0.0.1:5000 on the device/browser.")
    app.run(host="0.0.0.0", port=5000, debug=False)
