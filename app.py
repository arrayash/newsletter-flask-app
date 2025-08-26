# File: app.py
# Description: Defines the Flask application, Subscriber model, and web routes
#              for handling subscription links from the newsletter email.
# (Final Version with Attractive HTML/CSS Pages)

import os
from flask import Flask, render_template_string
from flask_sqlalchemy import SQLAlchemy

# --- NEW: HTML Template for All Response Pages ---
RESPONSE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Neo Safe2Eat Newsletter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #0c1a24;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .container {
            background-color: #115e59;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #2CC3DA;
            width: 100%;
        }
        h1 { 
            color: #FFFFFF; 
            margin-bottom: 20px;
            font-family: 'Courier New', Courier, monospace;
            letter-spacing: 2px;
        }
        .message-box {
            color: white; 
            padding: 20px; 
            border-radius: 8px; 
            margin: 20px 0;
            border-left: 5px solid;
        }
        .message-box.success { background-color: rgba(40, 167, 69, 0.2); border-color: #28a745; }
        .message-box.info { background-color: rgba(23, 162, 184, 0.2); border-color: #17a2b8; }
        .message-box.warning { background-color: rgba(255, 193, 7, 0.2); border-color: #ffc107; }
        .btn {
            display: inline-block;
            background-color: #2CC3DA;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }
        .btn:hover { background-color: #1aa3ba; }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #2CC3DA;
            font-size: 12px;
            color: #bdc5d1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }}</h1>
        <div class="message-box {{ message_type }}">
            <p style="margin: 0;">{{ description }}</p>
        </div>
        
        <a href="https://www.neophyte.ai" class="btn">Visit Our Website</a>
        
        <div class="footer">
            <p><strong>Neo Safe2Eat</strong> - Your trusted source for food safety intelligence</p>
            <p>© 2025 Neophyte Ambient Intelligence</p>
        </div>
    </div>
</body>
</html>
"""

# --- 1. App and DB Configuration (PostgreSQL Ready) ---
app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'subscribers.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- 2. Database Model ---
class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed = db.Column(db.Boolean, default=True, nullable=False)


# --- 3. Web Routes (Updated with Attractive Templates) ---
@app.route('/')
def index():
    context = {
        'title': "Neo Safe2Eat",
        'message_type': "info",
        'description': "This is the subscription management service for our weekly newsletter on food safety, quality & traceability."
    }
    return render_template_string(RESPONSE_TEMPLATE, **context)

@app.route('/subscribe/<email>', methods=['GET'])
def subscribe(email):
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber:
        subscriber.subscribed = True
        db.session.commit()
        context = {
            'title': "🎉 Welcome Back!",
            'message_type': "success",
            'description': "Thank you for re-subscribing. You'll continue to receive our weekly food safety updates."
        }
    else:
        new_subscriber = Subscriber(email=email, subscribed=True)
        db.session.add(new_subscriber)
        db.session.commit()
        context = {
            'title': "✅ Subscription Successful!",
            'message_type': "success",
            'description': "Thank you for subscribing to the Neo Safe2Eat Newsletter! Keep an eye on your inbox."
        }
    return render_template_string(RESPONSE_TEMPLATE, **context)

@app.route('/unsubscribe/<email>', methods=['GET'])
def unsubscribe(email):
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber:
        subscriber.subscribed = False
        db.session.commit()
        context = {
            'title': "✅ Unsubscribed",
            'message_type': "info",
            'description': "You have been successfully unsubscribed. We're sorry to see you go!"
        }
    else:
        context = {
            'title': "🤔 Already Unsubscribed",
            'message_type': "warning",
            'description': "Your email was not found in our subscriber list, so you are already unsubscribed."
        }
    return render_template_string(RESPONSE_TEMPLATE, **context)


# --- 4. Command Line Interface (CLI) for local DB setup ---
@app.cli.command('init-db')
def init_db_command():
    db.create_all()
    print("Initialized the local database.")


# --- FINAL FIX: Automatically create database tables on startup ---
with app.app.context():
    db.create_all()


# --- 5. Main Execution Block (for local development) ---
if __name__ == '__main__':
    app.run(debug=True)