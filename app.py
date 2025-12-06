from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from database import init_db, add_tracker, list_trackers, store_positions, get_positions

# 👉 Your real Bearer Token temporarily hardcoded here
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImNsaWVudDIwMjUifQ.e2AQAFvYAnWLM3cC0_wRzBLkUPiEighd8zkNl3jyB94"
API_URL = "http://98.93.133.125:3000/position"

app = Flask(__name__)
CORS(app)

init_db()

def update_tracker(serial):
    print(f"\n🔄 Updating tracker {serial} ...")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    payload = {"serialNumber": serial}

    print(f"➡ Sending request for serial: {serial}")
    response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
    print(f"⬅ Status: {response.status_code}")

    if response.status_code != 200:
        print("❌ API returned error:", response.text)
        return

    try:
        data = response.json()
        print(f"📡 Received {len(data)} points from API")
    except Exception as e:
        print("❌ JSON decode error:", e)
        print("Raw response:", response.text)
        return

    store_positions(serial, data)
    print(f"💾 Stored up to {len(data)} new points for {serial}")

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
def trackers():
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
        "features": features
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"🚀 Flask backend starting on port {port}")
    app.run(host="0.0.0.0", port=port)
