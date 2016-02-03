from views import db
from models import Task
from datetime import date

db.create_all()
db.session.add(Task("Finish this tutorial",date(2015,3,13),10,1))
db.session.add(Task("Finish RealPython 2 tutorial",date(2015,4,13),10,1))

db.session.commit()