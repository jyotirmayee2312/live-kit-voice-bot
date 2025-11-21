from flask import Flask, jsonify, request
from flask_cors import CORS
import os, jwt, time
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv(dotenv_path=".env")

app = Flask(__name__)
CORS(app)

# Read keys from env
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "").strip()
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "").strip()
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "").strip()  # must be wss://

print("=== SERVER STARTUP ===")
print("API_KEY:", LIVEKIT_API_KEY)
print("SECRET:", (LIVEKIT_API_SECRET or "")[:5] + "...")
print("URL:", LIVEKIT_URL)
print("======================")

@app.route("/getToken")
def get_token():
    identity = request.args.get("identity", "guest")
    room = request.args.get("room", "room-123")

    payload = {
        "iss": LIVEKIT_API_KEY,
        "sub": identity,
        "exp": int(time.time()) + 3600,  # 1 hour expiry
        "video": {
            "room": room,
            "roomJoin": True,
            "canPublish": True,
            "canSubscribe": True
        }
}


    token = jwt.encode(payload, LIVEKIT_API_SECRET, algorithm="HS256")



    # 🔎 Debug prints
    print(f"[DEBUG] Identity: {identity}")
    print(f"[DEBUG] Room: {room}")
    print(f"[DEBUG] Payload: {payload}")
    print(f"[DEBUG] Token (first 40 chars): {token[:40]}...")
    print(f"[DEBUG] URL returned to frontend: {LIVEKIT_URL}")

    return jsonify({
        "url": LIVEKIT_URL,
        "token": token
    })

if __name__ == "__main__":
    # Run on all interfaces so frontend can reach it
    app.run(host="0.0.0.0", port=5000, debug=True)
