#imports
from flask import Flask, render_template, flash, redirect, url_for, request, session, g
import sqlite3
from functools import wraps
from forms import AddTaskForm, RegisterForm, LoginForm
from flask.ext.sqlalchemy import SQLAlchemy


#config
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import *

#helper functions

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
	form = LoginForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			user = User.query.filter_by(name=request.form['name']).first()
			if user is not None and user.password == request.form["password"]:
				session["logged_in"] = True
				flash("welcome")
				return redirect(url_for('tasks'))
			else:
				error = "Wrong credential, Try again"
		else:
			error = "Both fields are required"
	return render_template("login.html", form=form, error=error)



@app.route('/tasks/') #show tasks
@login_required
def tasks():
	open_tasks = db.session.query(Task).filter_by(status='1')\
	.order_by(Task.due_date.asc())
	closed_tasks = db.session.query(Task).filter_by(status='0')\
	.order_by(Task.due_date.asc())
	return render_template('tasks.html',form=AddTaskForm(request.form),\
		open_tasks=open_tasks,closed_tasks=closed_tasks)

@app.route('/add/', methods=['GET','POST'])
@login_required
def new_task():
	form = AddTaskForm(request.form)
	if request.method == 'POST':
		if form.validate_on_submit():
			new_task = Task(form.name.data,form.due_date.data,form.priority.data,'1')
			db.session.add(new_task)
			db.session.commit()
			flash("New entry successfully added Thanks !")
	return redirect(url_for('tasks'))

@app.route('/complete/<int:task_id>') #update task
@login_required
def complete(task_id):
	new_id = task_id
	db.session.query(Task).filter_by(task_id=new_id).update\
	({"status":"0"})
	db.session.commit()
	flash('The task is complete')
	return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>')
@login_required
def delete_entry(task_id):
	new_id = task_id
	db.session.query(Task).filter_by(task_id=new_id).delete()
	db.session.commit()
	flash("The task has been deleted")
	return redirect(url_for('tasks'))

@app.route('/register/', methods=['GET','POST'])
def register():
	error = None
	form = RegisterForm(request.form)
	if request.method == 'POST':
		print form.validate_on_submit()
		if form.validate_on_submit():
			new_user = User(\
				form.name.data,
				form.email.data,
				form.password.data,)
			db.session.add(new_user)
			db.session.commit()
			flash("Thanks for registering. Please Login")
			return redirect(url_for('login'))
	return render_template('register.html', form=form, error=error)












