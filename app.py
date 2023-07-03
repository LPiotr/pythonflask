from flask import Flask, render_template, request, redirect, url_for, session, Response
from gevent.pywsgi import WSGIServer
from flask_mysqldb import MySQL
#import redis
import MySQLdb.cursors
from datetime import datetime
import time
import json
import re
import locale

locale.setlocale(locale.LC_TIME, 'pl_PL')

app = Flask(__name__)
# r = redis.Redis(host='192.168.100.18', port=6379, db=0, charset='utf-8')

app.secret_key = 'xyzsdfg'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

mysql = MySQL(app)


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Zalogowano pomyślnie!'
            return redirect(url_for('users'))
        else:
            message = 'Proszę wprowadź poprawny email lub hasło!'
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('dashboard'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Konto z podanym adresem {} istnieje w bazie!'.format(
                email)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Nieprawidłowy adres email!'
        elif not userName or not password or not email:
            message = 'Proszę wypełnić formularz!'
        else:
            cursor.execute(
                'INSERT INTO users VALUES (NULL, %s, %s, %s)', (userName, password, email,))
            mysql.connection.commit()
            message = 'Pomyślnie zarejestrowano nowego użytkownika {}!'.format(
                userName)
    elif request.method == 'POST':
        message = 'Proszę wypełnić formularz!'
    return render_template('register.html', message=message)


@app.route("/listen")
def listen():
    def respond_to_client():
        while True:
            global current_time
            current_time = datetime.now().strftime("%c")
            _data = json.dumps({"clock": current_time})
            yield f"id: 1\ndata: {_data}\nevent: online\n\n"
            time.sleep(0.5)
    return Response(respond_to_client(), mimetype='text/event-stream')


@app.route('/users')
def users():
    if 'loggedin' in session:
        with open('users.json', 'r') as file:
            users = json.load(file)
    
        return render_template('users.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)
    http_server = WSGIServer(("localhost", 80), app)
    http_server.serve_forever()