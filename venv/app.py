from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
# dotenv_path = os.path.join(os.path.dirname(__file__), 'environment.env')
# load_dotenv(dotenv_path)
# os.environ['SECRET_KEY'] = '27012001ma'
# secret_key = os.getenv('SECRET_KEY')
app=Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/mhmdz/OneDrive/Bureau/QuizTestFlask/venv/var/app-instance/users.db'
db = SQLAlchemy(app)
app.secret_key = "hello"
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(120), unique=True, nullable=False)
    password =db.Column(db.String(80), nullable=False)

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False) 

with app.app_context():
    db.create_all()  # Create the necessary tables
    Exercise.query.delete()
    question1 = "What is the capital of France?"
    question2 = "What is the largest planet in our solar system?"
    question3 = "Who wrote the novel 'Pride and Prejudice'?"
    existing_exercises = Exercise.query.filter(Exercise.question.in_([question1, question2, question3])).all()
    existing_questions = [exercise.question for exercise in existing_exercises]
    # userFiras=User(userName='firas',password='firas123')
    if question1 not in existing_questions:
        exercise1 = Exercise(question=question1, answer="Paris")
        db.session.add(exercise1)
    
    if question2 not in existing_questions:
        exercise2 = Exercise(question=question2, answer="Jupiter")
        db.session.add(exercise2)
    
    if question3 not in existing_questions:
        exercise3 = Exercise(question=question3, answer="Jane Austen")
        db.session.add(exercise3)
    db.session.add_all([exercise1, exercise2, exercise3])
    # db.session.add(userFiras)
    db.session.commit()

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        newUser = User(userName=userName, password=password)
        db.session.add(newUser)
        db.session.commit()
        return '<h1 style="text-align: center;">Thank you for subscribing!</h1>' 
    return render_template('subscription.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        user = User.query.filter_by(userName=userName).first()
        if user and user.password == password:
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('respond'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')
@app.route('/users')
def view_users():
    users = User.query.all()
    exercises=Exercise.query.all()
    return render_template('index.html', users=users,exercises=exercises)

@app.route('/sendResponses', methods=['POST','GET'])
def respond():
    exercises = Exercise.query.all()
    score = 0
    for exercise in exercises:
        user_answer = request.form.get(str(exercise.id))
        if user_answer and exercise.answer and user_answer.lower() == exercise.answer.lower():
            score += 1
    # if score>0:
    if request.method == 'POST':
      return f"your score is {score}"
    return render_template('test.html', score=score, exercises=exercises)