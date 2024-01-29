from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from flask_migrate import Migrate
dotenv_path = os.path.join(os.path.dirname(__file__), 'environment.env')
load_dotenv(dotenv_path)
adminPassword=os.getenv('adminPassword')
adminName=os.getenv('adminName')
# os.environ['SECRET_KEY'] = '27012001ma'
# secret_key = os.getenv('SECRET_KEY')
app=Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/mhmdz/OneDrive/Bureau/QuizTestFlask/venv/var/app-instance/users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.secret_key = "hello"
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(120), unique=True, nullable=False)
    password =db.Column(db.String(80), nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)
    total_score = db.Column(db.Integer)

class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)

class Exercise(db.Model):
    __tablename__ = 'exercise'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False) 

class Suggestion(db.Model):
    __tablename__ = 'suggestion'
    id = db.Column(db.Integer, primary_key=True)
    userId= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)

with app.app_context():
    db.create_all()  
    question1 = "What is the capital of France?"
    question2 = "What is the largest planet in our solar system?"
    question3 = "Who wrote the novel 'Pride and Prejudice'?"
    
    existing_exercises = Exercise.query.filter(Exercise.question.in_([question1, question2, question3])).all()
    existing_questions = [exercise.question for exercise in existing_exercises]
    
    if question1 not in existing_questions:
        exercise1 = Exercise(question=question1, answer="Paris")
        db.session.add(exercise1)
    
    if question2 not in existing_questions:
        exercise2 = Exercise(question=question2, answer="Jupiter")
        db.session.add(exercise2)
    
    if question3 not in existing_questions:
        exercise3 = Exercise(question=question3, answer="Jane Austen")
        db.session.add(exercise3)
    
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
        if userName == 'admin':
                return redirect(url_for('admin'))
        if user and user.password == password:
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('respond'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')
@app.route('/')
def view_users():
    calculate_total_score()
    top_users = get_top_users()
    users = User.query.all()
    exercises = Exercise.query.all()
    scores = Score.query.all()
    suggestions=Suggestion.query.all()
    return render_template('index.html', users=users, exercises=exercises, scores=scores, top_users=top_users,suggestions=suggestions)

@app.route('/sendResponses', methods=['POST','GET'])
def respond():
    user_id=session.get('user_id')
    exercises = Exercise.query.all()
    score = 0
    for exercise in exercises:
        user_answer = request.form.get(str(exercise.id))
        if user_answer and exercise.answer and user_answer.lower() == exercise.answer.lower():
            score += 1
    # if score>0:
    if request.method == 'POST':
      new_score=Score(userId=user_id,score=score)
      db.session.add(new_score)
      db.session.commit()
      return f"your score is {score}"
    return render_template('test.html', score=score, exercises=exercises)

def calculate_total_score():
    users = User.query.all()
    for user in users:
        scores = Score.query.filter_by(userId=user.id).all()
        total_score = sum(score.score for score in scores)
        user.total_score = total_score
    db.session.commit()


def get_top_users():
    top_users= User.query.order_by(User.total_score.desc()).limit(3).all()
    return top_users

@app.route('/submit_question', methods=['POST','GET'])
def submit_question():
    if request.method == 'POST':
        userId=session.get('user_id')
        question = request.form.get('question')
        response = request.form.get('response')
        new_suggestion=Suggestion(userId=userId,question=question,answer=response)
        db.session.add(new_suggestion)
        db.session.commit()
        return "added to suggestions waiting for approval" 
    return render_template('addTest.html')

@app.route('/admin', methods=['POST','GET'])
def admin():
    suggestions=Suggestion.query.all()
    if request.method == 'POST':
        suggestion_id = request.form['suggestion_id']  # Get the ID of the approved suggestion
        suggestion = Suggestion.query.get(suggestion_id) 
        if suggestion:
            # Create a new Exercise using the approved suggestion
            exercise = Exercise(question=suggestion.question, answer=suggestion.answer)
            db.session.add(exercise)
            db.session.commit()
            db.session.delete(suggestion)
            db.session.commit()
            user = User.query.get(suggestion.userId)
            if user:
                # Increment the user's total score by 10
                score= 10
                db.session.commit()
                new_score=Score(userId=user.user_id,score=score)
                db.session.add(new_score)
                db.session.commit()
    return render_template('suggestions.html',suggestions=suggestions)


# @app.route('/admin', methods=['POST','GET'])
# def admin():
#     userId = session.get('user_id')
#     user = User.query.get(userId)
#     suggestions = []

#     # Check if the user is logged in and is an admin
#     if user and user.userName == adminName and user.password == adminPassword:
#         suggestions = Suggestion.query.all()

#         if request.method == 'POST':
#             suggestion_id = request.form['suggestion_id']
#             suggestion = Suggestion.query.get(suggestion_id)

#             if suggestion:
#                 # Create a new Exercise using the approved suggestion
#                 exercise = Exercise(question=suggestion.question, answer=suggestion.answer)
#                 db.session.add(exercise)
#                 db.session.commit()

#                 db.session.delete(suggestion)
#                 db.session.commit()

#                 user = User.query.get(suggestion.userId)
#                 if user:
#                     # Increment the user's total score by 10
#                     user.total_score += 10
#                     db.session.commit()

#                 new_score = Score(userId=user.id, score=user.total_score)
#                 db.session.add(new_score)
#                 db.session.commit()

#         return render_template('suggestions.html', suggestions=suggestions)

