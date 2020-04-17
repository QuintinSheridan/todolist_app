import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# get secrets stored as local bash environment variables
# In bash, define variebles eg.: ~$ USERNAME='user1'
# export all variables you want access to eg.: ~$ export USERNAME 

user = os.environ['USERNAME']
pword = os.environ['PW']
db_name = os.environ['DB']

#print(f'user: {user}, pword: {pword}, db:{db}')

app = Flask(__name__)
sqlurl = f'postgres://{user}:{pword}@localhost:5432/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlurl
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False, default=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

# migrations will be sued for updating the db
#db.create_all()

@app.route('/todos/create', methods=['POST'])
def create_todo():
  body={}
  error = False
  try:
    description = request.get_json()['description']
    print(f'description: {description}')
    todo = Todo(description=description)
    print('Todo object created')
    db.session.add(todo)
    print('Todo object added to session')
    db.session.commit()
    print('session committed')
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def update_completed(todo_id):
  print(f'todo_id: {todo_id}')
  try:
    print('trying to get completed')
    completed = request.get_json()['completed']
    print(f'completed: {completed}')
    todo = Todo.query.get(todo_id)
    print(f'todo.completed: {todo.completed}')
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/<todo_id>/delete', methods=['POST'])
def delete(todo_id):
  print(f'Deleting Todo {todo_id}')
  try:
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

  
  

@app.route('/')
def index():
  return render_template('index.html', data=Todo.query.order_by('id').all())