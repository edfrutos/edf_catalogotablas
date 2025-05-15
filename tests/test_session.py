from flask import Flask, session, redirect, url_for, request

app = Flask(__name__)
app.secret_key = 'clave-secreta-prueba'

@app.route('/')
def index():
    if 'user' in session:
        return f'Logueado como {session["user"]}'
    return 'No logueado'

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['user']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <input type="text" name="user">
            <input type="submit">
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index')) 