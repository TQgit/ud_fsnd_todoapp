import sys
from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:demo@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<todo id:{self.id}, description:{self.description}>'


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', cascade='all, delete-orphan', lazy=True)


@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        list = TodoList(name=name)
        db.session.add(list)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, list_id=list_id)
        db.session.add(todo)
        db.session.commit()
    except:
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))


@app.route('/lists/<list_id>/delete-list', methods=['DELETE'])
def delete_list(list_id):
    try:
        db.session.delete(TodoList.query.get(list_id))
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return {}


@app.route('/todos/<todo_id>/delete-todo', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        db.session.delete(Todo.query.get(todo_id))
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return {}


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', lists=TodoList.query.all(), active_list=TodoList.query.get(list_id),
           todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))
