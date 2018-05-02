from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == "__main__":
    context = ('www.cryptoexamples.com.cert.pem', 'www.cryptoexamples.com.key.pem')
    app.run(host='0.0.0.0', port=80, ssl_context=context, threaded=True, debug=True)
