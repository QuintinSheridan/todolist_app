import os
import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
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

#############
# DB MODELS #
#############

class TodoList(db.Model):
  __tablename__ = 'todolists'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False)
  todos = db.relationship('Todo', cascade="all,delete", backref='list', lazy=True)


class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)
  completed = db.Column(db.Boolean, nullable=False)
  list_id = db.Column(db.Integer, db.ForeignKey('todolists.id', ondelete='CASCADE'), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

##################
# Route Handlers #
##################

# list creation
@app.route('/lists/create', methods=['POST'])
def create_list():
  print('Tyring to make a list')
  error = False
  body = {}
  try:
    print('hello')
    name = request.get_json()['name']
    print('bob')
    todo_list = TodoList(name=name, completed=False)
    db.session.add(todo_list)
    db.session.commit()
    body['id'] = todo_list.id
    body['name'] = todo_list.name
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

# list completion
@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo_list = TodoList.query.get(list_id)
    todo_list.completed = completed
    list_todos = todo_list.todos
    for todo in list_todos:
      todo.completed= completed
    print(f'list_todos: {list_todos}')
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))


# list deletion
# @app.route('/lists/<list_id>', methods=['DELETE'])
# def delete_list(list_id):
#   print('Trying to delete a list')
#   try:
#     TodoList.query.filter_by(id=list_id).delete()
#     db.session.commit()
#   except Exception as e:
#     print(f'The following exception occured while deleting a list: {e}')
#     db.session.rollback()
#   finally:

#     db.session.close()
#   return jsonify({ 'success': True })

#list deletion
@app.route('/lists/delete/<list_id>', methods=['GET', 'DELETE'])
def delete_list(list_id):
  print(f'\n\n\n Trying to delete list_id {list_id}')
  try:
    TodoList.query.filter_by(id=list_id).delete()
    db.session.commit()
  except Exception as e:
    print(f'The following exception occured while deleting a list: {e}')
    db.session.rollback()
  finally:
    db.session.close()
    lists = TodoList.query.order_by(TodoList.id).all()
    print(f'\n\n\n after deletion lists: {lists}')

  lists = TodoList.query.order_by(TodoList.id).all()
  print(f'\n\n\n lists: {lists}')
  if lists:
    first_list = lists[0].id
    print(first_list)
    return redirect(f'/lists/{first_list}')
  else:
    return render_template('index.html', todos=None, lists=None, active_list_name=None, active_list_id = None)

# note: more conventionally, we would write a
# POST endpoint to /todos for the create endpoint:
# @app.route('/todos', method=['POST'])
@app.route('/todos/<list_id>/create', methods=['POST'])
def create_todo(list_id):
  print(f'Creating todo for list {list_id}')
  error = False
  body = {}
  try:
    print('hello')
    description = request.get_json()['description']
    print('bob')
    todo = Todo(description=description, completed=False, list_id=list_id)
    db.session.add(todo)
    db.session.commit()
    body['id'] = todo.id
    body['completed'] = todo.completed
    body['description'] = todo.description
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })


# @app.route('/lists/<list_id>')
# def get_list_todos(list_id):
#   lists = TodoList.query.order_by(TodoList.id).all()
#   list_exists=False
#   print(f'list_id: {list_id}')
#   for todolist in lists:
#     print(f'list.id {todolist.id}')
#     if todolist.id == list_id:
#       list_exists = True
#   if list_exists:
#     active_list_name =  TodoList.query.get(list_id).name
#     active_list_id = list_id
#     for todolist in lists:
#       print(f'list name {todolist.name}')
#       todos = Todo.query.filter_by(list_id=list_id).order_by(Todo.id)
#   else:
#     active_list_name =  None
#     active_list_id = None
#     todos=None
#     print(f'todos={todos}, lists={lists}, active_list_name={active_list_name}, active_list_id={active_list_id}')
#   return render_template('index.html', todos=todos, lists=lists, active_list_name=active_list_name, active_list_id = active_list_id)

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  print(f'Getting todos for list {list_id}')
  lists = TodoList.query.order_by(TodoList.id).all()
  active_list_name =  TodoList.query.get(list_id).name
  active_list_id = list_id
  todos = Todo.query.filter_by(list_id=list_id).order_by(Todo.id)
  print(f'todos={todos}, lists={lists}, active_list_name={active_list_name}, active_list_id={active_list_id}')
  return render_template('index.html', todos=todos, lists=lists, active_list_name=active_list_name, active_list_id = active_list_id)

@app.route('/')
def index():
  lists = TodoList.query.order_by(TodoList.id).all()
  print(f'\n\n\n lists: {lists}')
  if lists:
    first_list = lists[0].id
    return redirect(f'/lists/{first_list}')
  else:
    return render_template('index.html', todos=None, lists=None, active_list_name=None, active_list_id = None)