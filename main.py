from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import re

app = Flask(__name__)
bcrypt = Bcrypt(app)

#database connection details
app.config['MYSQL_HOST'] = 'your hostname'
app.config['MYSQL_USER'] = 'your username'
app.config['MYSQL_PASSWORD'] = 'your password'
app.config['MYSQL_DB'] = 'database name you created'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'your secret key'

#mysql initialization
db = MySQL(app)

#signin-index.html routing
@app.route('/', methods=['GET', 'POST'])
def signin():
    msg=''
    # Check if "username" and "password" POST requests exist
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        user_password = request.form['password']
        # Check if account exists using MySQL
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cur.fetchone()
        if account:
            password = account['password']
            if bcrypt.check_password_hash(password.encode('utf-8'), user_password.encode('utf-8')):
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect('/home/')
            else:
                # Account doesnt exist or username/password incorrect
                msg = 'Incorrect username or password!'
        cur.close()
    # Show the login form
    return render_template('/index.html/', msg=msg)

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    msg=""
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'confirm_password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['confirm_password']
        email = request.form['email']
        # Check if account exists using MySQL
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cur.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        elif password != password_check:
            msg = 'Passwords do not match'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table and hash password
            pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, pw_hash, email))
            db.connection.commit()
            cur.close()
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
    return redirect('/')

# http://localhost:5000/home - this will be the home page, only accessible for signed in users
@app.route('/home/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show home page
        return render_template('home.html', username=session['username'])
    else:
        # User is not loggedin redirect to login page
        return redirect('/')

# http://localhost:5000/profile - this will be the profile page, only accessible for signed in users
@app.route('/profile/')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        username = session['username']
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cur.fetchone()
        # User is loggedin show my profile
        return render_template('profile.html', username=session['username'], email=account['email'], password=account['password'])
    else:
        # User is not loggedin redirect to login page
        return redirect('/')

# http://localhost:5000/update - this will be the update profile page, only accessible for signed in users
@app.route('/update/', methods=['GET', 'POST'])
def update():
    msg=""
    if 'loggedin' in session:
        if request.method == 'POST' and 'address' in request.form and 'birthday' in request.form:
            username = session['username']
            address = request.form['address']
            birthday = request.form['birthday']
            cur = db.connection.cursor()
            cur.execute('UPDATE accounts SET address = %s, birthday = %s where username = %s', (address, birthday, username))
            db.connection.commit()
            cur.close()
            msg = 'Update successful!'
        return render_template('update.html', username=session['username'], msg=msg)
    else:
        # User is not loggedin redirect to login page
        return redirect('/')

# http://localhost:5000/followers - this will be the follower page, only accessible for signed in users
@app.route('/followers/')
def followers():
    if 'loggedin' in session:
        username = session['username']
        cur = db.connection.cursor()
        cur.execute('SELECT * from accounts WHERE username = %s', (username,))
        account = cur.fetchone()
        follower_id = account['id']
        cur.execute('SELECT followed_id from followers where follower_id = %s', (follower_id,))
        followed = cur.fetchall()
        num = len(followed)
        cur.execute('SELECT followed_username from followers WHERE follower_id = %s', (follower_id,))
        followed_username = cur.fetchall()
        return render_template('followers.html', username=session['username'], num=num, usernames=followed_username)
    else:
        # User is not loggedin redirect to login page
        return redirect('/')

# http://localhost:5000/follow - follow a friend page, only accessible for signed in users
@app.route('/follow/', methods=['GET', 'POST'])
def follow():
    msg=""
    if 'loggedin' in session:
        if request.method == 'POST' and 'username' in request.form:
            username=session['username']
            followed_username = request.form['username']
            cur = db.connection.cursor()
            cur.execute('SELECT * FROM accounts WHERE username = %s', (followed_username,))
            account = cur.fetchone()
            if account:
                followed_id = account['id']
                cur.execute('SELECT * FROM accounts WHERE username = %s', (username,))
                account2 = cur.fetchone()
                follower_id = account2['id']
                cur.execute('INSERT INTO followers VALUES (NULL, %s, %s, %s)', (follower_id, followed_id, followed_username))
                msg = "Success"
            else:
                msg = "Wrong username"
            db.connection.commit()
            cur.close()
        return render_template('follow.html', username=session['username'], msg=msg)
    else:
        # User is not loggedin redirect to login page
        return redirect('/')

if __name__ == '__main__':
   app.run()