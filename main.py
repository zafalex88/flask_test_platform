from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

#database connection details
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'flask_test_1'
app.secret_key = 'my secret key'

#mysql initialization
mysql = MySQL(app)

#login-index.html routing
@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template('/index.html/')

@app.route('/register/', methods=['GET', 'POST'])
def register():
    return render_template('/register.html/')
