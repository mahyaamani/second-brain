"""VocalBridge voice agent prototype — Flask backend."""

import os
import requests
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv(override=True)

from config import VOCAL_BRIDGE_API_KEY, VOCAL_BRIDGE_URL, VOCAL_BRIDGE_AGENT_ID

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/voice-token", methods=["POST"])
def voice_token():
    if not VOCAL_BRIDGE_API_KEY:
        return jsonify({"error": "VOCAL_BRIDGE_API_KEY not set"}), 500

    try:
        resp = requests.post(
            f"{VOCAL_BRIDGE_URL}/api/v1/token",
            headers={
                "X-API-Key": VOCAL_BRIDGE_API_KEY,
                "Content-Type": "application/json",
                **({"X-Agent-Id": VOCAL_BRIDGE_AGENT_ID} if VOCAL_BRIDGE_AGENT_ID else {}),
            },
            json={"participant_name": "User"},
            timeout=10,
        )
        if not resp.ok:
            app.logger.error("VocalBridge responded %s: %s", resp.status_code, resp.text)
            return jsonify({"error": f"VocalBridge error: {resp.status_code}", "detail": resp.text}), resp.status_code
        return jsonify(resp.json())
    except requests.exceptions.Timeout:
        return jsonify({"error": "VocalBridge API timed out"}), 504
    except requests.exceptions.RequestException as e:
        app.logger.error("Token request failed: %s", e)
        return jsonify({"error": "Failed to get voice token"}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
