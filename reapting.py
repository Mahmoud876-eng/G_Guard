import time
import json
import random
import requests
import sseclient
from flask import Flask, render_template, jsonify

FIREBASE_BASE = "https://synaptix-e0fa0-default-rtdb.europe-west1.firebasedatabase.app"

    
# Flask app setup
app = Flask(__name__)
@app.route('/', methods=["GET"])
def index():
    url = f"{FIREBASE_BASE}/data.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        latest_data = resp.json() or {}
    except Exception as e:
        print(f"[reapting] fetch error: {e}")
        latest_data = {}

    co2_value = latest_data.get("CO2", 0)
    humidity_value = latest_data.get("humidity", 0)
    temperature_value = latest_data.get("temperature", 0)
    return render_template(
        "dashboard.html",
        co2_value=co2_value,
        humidity_value=humidity_value,
        temperature_value=temperature_value,
        latest_json=latest_data,
    )


@app.route('/api/data', methods=["GET"]) 
def api_data():
    """Return current Firebase snapshot as JSON (same-origin for polling)."""
    url = f"{FIREBASE_BASE}/data.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        payload = resp.json() or {}
        return jsonify({
            "success": True,
            "data": payload,
        })
    except Exception as e:
        print(f"[reapting] api_data error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
        }), 500

if __name__ == "__main__":
    app.run(debug=True)