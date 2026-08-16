from flask import Flask,jsonify
import os
from pyngrok import ngrok
from flask_cors import CORS

NGROK_AUTH_TOKEN='30k6PIYyYSdLcsasr6QFHiPhQsl_6AnDnpjAv8mp5bCaq5vAc'

app = Flask(__name__)
CORS(app)


@app.route('/api/hello',methods=['GET'])
def hello():
    return jsonify({'message':'hello from Mac via Terminal'})


if __name__=='__main__':
    port = 7001
    os.environ['FLASK_ENV'] = 'development'

    ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    public_url = ngrok.connect(port)
    print(f"Public URL:{public_url}/api/hello \n \n")

    app.run(port=port)