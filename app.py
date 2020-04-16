import os
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# get secrets stored as local bash environment variables
# In bash, define variebles eg.: ~$ USERNAME='user1'
# export all variables you want access to eg.: ~$ export USERNAME 

user = os.environ['USERNAME']
pword = os.environ['PW']
db = os.environ['DB']

#print(f'user: {user}, pword: {pword}, db:{db}')

app = Flask(__name__)
sqlurl = f'postgres://{user}:{pword}@localhost:5432/{db}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlurl
db = SQLAlchemy(app)

class Todo(db.Model):
  __tablename__ = 'todos'
  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(), nullable=False)

  def __repr__(self):
    return f'<Todo {self.id} {self.description}>'

db.create_all()

@app.route('/todos/create', methods=['POST'])
def create_todo():
  description = request.get_json()['description']
  todo = Todo(description=description)
  db.session.add(todo)
  db.session.commit()
  return jsonify({
    'description': todo.description
  })


@app.route('/')
def index():
  return render_template('index.html', data=Todo.query.all())