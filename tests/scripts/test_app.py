from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "¡Hola, mundo! Prueba de servidor Gunicorn funcionando."

@app.route('/health')
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=False)
