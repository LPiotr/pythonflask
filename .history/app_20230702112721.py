from flask import Flask, render_template, request, redirect, url_for, session
from flask_sse import sse
from apscheduler.schedulers.background import BackgroundScheduler

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import json  

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost"
app.register_blueprint(sse, url_prefix='/stream')

app.secret_key = 'xyzsdfg'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
  
mysql = MySQL(app)
  

try:
    with open('users.json', 'r') as file:
        users = json.load(file)
except FileNotFoundError:
    pass

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            mesage = 'Zalogowano pomyślnie !'
            return render_template('user.html', mesage = mesage)
        else:
            mesage = 'Proszę wprowadż poprawny email lub hasło !'
    return render_template('login.html', mesage = mesage)
  
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))
  
@app.route('/register', methods =['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Konto z podanym adresem {} istnieje w bazie !'.format(email)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Nieprawidłowy adres email !'
        elif not userName or not password or not email:
            mesage = 'Proszę wypełnić formularz !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (userName, password, email ))
            mysql.connection.commit()
            mesage = 'Pomyślnie zarejestrowano nowego użytkownika {}!'.format(userName)
    elif request.method == 'POST':
        mesage = 'Proszę wypełnić formularz !'
    return render_template('register.html', mesage = mesage)
    
if __name__ == "__main__":
    app.run()