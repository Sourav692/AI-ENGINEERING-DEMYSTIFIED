from flask import Flask, jsonify    
from flask_cors import CORS
from pyngrok import ngrok
import os
import sys

NGROK_AUTH_TOKEN = "30k6PIYyYSdLcsasr6QFHiPhQsl_6AnDnpjAv8mp5bCaq5vAc"  # Replace with your actual token

app = Flask(__name__)
CORS(app)

@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello from your Mac via public internet!"})

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Server is running!", "endpoint": "/api/hello"})

if __name__ == "__main__":
    port = 5000
    os.environ["FLASK_ENV"] = "development"

    try:
        print("🔐 Authenticating with ngrok...")
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)

        print("🌍 Creating public tunnel...")
        public_url = ngrok.connect(port)  # ← FIXED HERE

        print(f"\n✅ SUCCESS!")
        print(f"🌐 Public URL: {public_url}")
        print(f"🎯 API Endpoint: {public_url}/api/hello")
        print(f"🏠 Home: {public_url}/")
        print(f"📱 Test in browser or curl: curl {public_url}/api/hello\n")

        print("🚀 Starting Flask server...")
        app.run(port=port, debug=True)

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Get fresh auth token: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("2. Check ngrok account limits (bandwidth, tunnels)")
        print("3. Ensure no other ngrok processes are running")
        print("4. Try: ngrok kill")
        sys.exit(1)
