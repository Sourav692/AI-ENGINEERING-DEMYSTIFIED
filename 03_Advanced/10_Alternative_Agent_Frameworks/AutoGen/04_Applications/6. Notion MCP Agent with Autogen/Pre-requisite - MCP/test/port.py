from flask import Flask, jsonify
from flask_cors import CORS
from pyngrok import ngrok
import os

# ✅ Set your authtoken here or configure via terminal: ngrok config add-authtoken <token>
NGROK_AUTH_TOKEN = "30k6PIYyYSdLcsasr6QFHiPhQsl_6AnDnpjAv8mp5bCaq5vAc"

app = Flask(__name__)
CORS(app, expose_headers=["ngrok-skip-browser-warning"])
 # Allow public cross-origin access

@app.route("/api/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Hello from your Mac via public internet!"})

if __name__ == "__main__":
    port = 5000
    os.environ["FLASK_ENV"] = "development"
    
    # 🔐 Authenticate with Ngrok
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)

    # 🌍 Open public tunnel
    public_url = ngrok.connect(port)
    print(f"\n🌐 Public URL: {public_url}/api/hello\n")

    # 🚀 Start Flask app
    app.run(port=port)
