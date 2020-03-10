from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

#database connection details
app.config['MYSQL_HOST'] = 'Alex-PC'
app.config['MYSQL_USER'] = 'alex'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'flask_test_1'
app.config["MYSQL_DATABASE_CURSORCLASS"] = "DictCursor"
app.secret_key = 'my_secret_key'

#mysql initialization
mysql = MySQL(app)

#signin-index.html routing
@app.route('/', methods=['GET', 'POST'])
def signin():
    msg=''
    # Check if "username" and "password" POST requests exist
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect('/home.html/')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username or password!'
    # Show the login form
    return render_template('/index.html/', msg=msg)

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    msg=""
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form
    return render_template('/signup.html/', msg=msg)

# http://localhost:5000/signout/ - sign out page
@app.route('/signout/')
def signout():
    # Remove session data
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect('/index.html/')

# http://localhost:5000/home - this will be the home page, only accessible for signed in users
@app.route('/home/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect('/index.html/')
