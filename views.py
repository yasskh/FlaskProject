#imports
from flask import Flask, render_template, flash, redirect, url_for, request, session
import sqlite3
from functools import wraps

#config
app = Flask(__name__)
app.config.from_object('_config')

#helper functions
def connect_db():
	return sqlite3.connect(app.config["DATABASE_PATH"])

def login_required(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if "logged_in" in session:
			return f(*args,**kwargs)
		else:
			flash("You need to be logged in first")
			return redirect(url_for('login'))
	return wrap

#routes handlers
@app.route('/logout')
def logout():
	session.clear()
	flash("you were logged out")
	return redirect(url_for('login'))

@app.route('/', methods=['POST','GET'])
def login():
	error = None
	if request.method == 'POST':
		if request.form['username'] != app.config['USERNAME'] or \
			request.form['password'] != app.config['PASSWORD']:
			error = "Wrong credential try again"
		else:
			session['logged_in'] = True
			flash("You were logged in")
			return redirect(url_for('tasks'))
	return render_template("login.html", error = error)
