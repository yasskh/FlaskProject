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

@app.route('/tasks/') #show tasks
@login_required
def tasks():
	g.db = connect_db()
	cur = g.db.execute("select name, due_date, priority, task_id from tasks where status=1")
	open_tasks = [dict(name=row[0],due_date=row[1],priority=row[2],task_id=row[3]) for row in cur.fetchall()]
	cur = g.db.execute("select name, due_date, priority, task_id from tasks where status=0")
	closed_tasks = [dict(name=row[0],due_date=row[1],priority=row[2],task_id=row[3]) for row in cur.fetchall()]
	g.db.close()
	return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks)

@app.route('/add/', methods=['POST']) #add tasks
@login_required
def new_task():
	g.db = connect_db()
	name = request.form['name']
	due_date = request.form['due_date']
	priority = request.form['priority']
	if not name or not due_date or not priority:
		flash("All fields are required")
		return redirect(url_for('tasks'))
	else:
		g.db.execute('insert into tasks(name,due_date,priority,status) values(?,?,?,1)', [name,due_date,priority])
		g.db.commit()
		g.db.close()
		flash('New entry successfully entred')
		return redirect(url_for('tasks'))

@app.route('/complete/<int:task_id>') #update task
@login_required
def complete(task_id):
	g.db = connect_db()
	g.db.execute('update tasks  set status = 0 where task_id='+str(task_id))
	g.db.commit()
	g.db.close()
	flash("The task was marked as complete")
	return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>')
@login_required
def delete_entry(task_id):
	g.db = connect_db()
	g.db.execute('delete from tasks  where task_id='+str(task_id))
	g.db.commit()
	g.db.close()
	flash("The task was deleted")
	return redirect(url_for('tasks'))











