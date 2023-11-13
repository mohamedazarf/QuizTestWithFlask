from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
app=Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/mhmdz/OneDrive/Bureau/QuizTestFlask/venv/var/app-instance/users.db'
db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(120), unique=True, nullable=False)
    password =db.Column(db.String(80), nullable=False)
with app.app_context():
    db.create_all()  # Create the necessary tables
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

@app.route('/users')
def view_users():
    users = User.query.all()
    return render_template('index.html', users=users)