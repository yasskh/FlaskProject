#imports
from flask import Flask, render_template, flash, redirect, url_for, request, session, g
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
@app.route('/logout/')
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

@app.route('/tasks/')
@login_required
def tasks():
	g.db = connect_db()
	cur = g.db.execute("select name, due_date, priority, task_id from tasks where status=1")
	open_tasks = [dict(name=row[0],due_date=row[1],priority=row[2],task_id=row[3]) for row in cur.fetchall()]
	cur = g.db.execute("select name, due_date, priority, task_id from tasks where status=0")
	closed_tasks = [dict(name=row[0],due_date=row[1],priority=row[2],task_id=row[3]) for row in cur.fetchall()]
	g.db.close()
	return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks)


















