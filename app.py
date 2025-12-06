from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from database import init_db, add_tracker, list_trackers, store_positions, get_positions

TOKEN = os.environ.get("TRACKER_TOKEN", "REPLACE_ME")
API_URL = "http://98.93.133.125:3000/position"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

init_db()

def update_tracker(serial):
    """Fetch & store latest tracker positions"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    payload = {"serialNumber": serial}

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            store_positions(serial, data)
        else:
            print(f"API error for {serial}: {response.status_code}")
    except Exception as e:
        print(f"Update failed for {serial}: {e}")

def update_all_trackers():
    """Poll API for all trackers periodically"""
    print("Updating all trackers...")
    for serial in list_trackers():
        update_tracker(serial)

# Auto-update every 60s
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_all_trackers, trigger="interval", seconds=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.route("/add/<serial>", methods=["GET", "POST"])
def add_tracker_route(serial):
    add_tracker(serial)
    update_tracker(serial)
    return jsonify({"added": serial})

@app.route("/update/<serial>", methods=["GET", "POST"])
def update_specific_route(serial):
    update_tracker(serial)
    return jsonify({"updated": serial})

@app.route("/trackers")
def trackers_route():
    return jsonify(list_trackers())

@app.route("/data/<serial>")
def data(serial):
    rows = get_positions(serial)
    features = []

    for (ts, lat, lng, conf) in rows:
        features.append({
            "type": "Feature",
            "properties": {
                "timestamp": ts,
                "confidence": conf
            },
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]
            }
        })

    return jsonify({
        "type": "FeatureCollection",
        "tracker": serial,
        "total": len(features),
        "features": features
    })

@app.route("/stats")
def stats():
    stats_data = {}
    for serial in list_trackers():
        rows = get_positions(serial)
        timestamps = [r[0] for r in rows]
        stats_data[serial] = {
            "points": len(rows),
            "first": min(timestamps) if timestamps else None,
            "last": max(timestamps) if timestamps else None,
        }
    return jsonify(stats_data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"API running on port: {port}")
    app.run(host="0.0.0.0", port=port)
