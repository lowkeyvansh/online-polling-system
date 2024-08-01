from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///polls.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.relationship('Option', backref='poll', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)

db.create_all()

@app.route('/')
def home():
    polls = Poll.query.all()
    return render_template('index.html', polls=polls)

@app.route('/poll/<int:id>')
def poll(id):
    poll = Poll.query.get_or_404(id)
    return render_template('poll.html', poll=poll)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        question = request.form['question']
        options = request.form.getlist('options')

        new_poll = Poll(question=question)
        db.session.add(new_poll)
        db.session.commit()

        for option_text in options:
            new_option = Option(text=option_text, poll_id=new_poll.id)
            db.session.add(new_option)
            db.session.commit()

        return redirect(url_for('home'))
    return render_template('add.html')

@app.route('/vote/<int:option_id>', methods=['POST'])
def vote(option_id):
    option = Option.query.get_or_404(option_id)
    option.votes += 1
    db.session.commit()
    return redirect(url_for('poll', id=option.poll_id))

@app.route('/api/polls', methods=['GET'])
def api_polls():
    polls = Poll.query.all()
    result = []
    for poll in polls:
        poll_data = {
            'id': poll.id,
            'question': poll.question,
            'options': [{'id': option.id, 'text': option.text, 'votes': option.votes} for option in poll.options]
        }
        result.append(poll_data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
