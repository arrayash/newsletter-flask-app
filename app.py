# File: app.py
# Description: Defines the Flask application, Subscriber model, and web routes
#              for handling subscription links from the newsletter email.

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# --- 1. App and DB Configuration ---
app = Flask(__name__)

# Get the database URL from the environment variable provided by Render.
# Fallback to a local SQLite database if the variable is not set.
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Local development fallback
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'subscribers.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 2. Database Model ---
class Subscriber(db.Model):
    """Represents a subscriber in the database."""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        status = "Active" if self.subscribed else "Inactive"
        return f"<Subscriber {self.email} - {status}>"

# --- 3. Web Routes (to handle clicks from email) ---
@app.route('/')
def index():
    """A simple index page to confirm the app is running."""
    return "Subscription management service is running."

@app.route('/subscribe/<email>', methods=['GET'])
def subscribe(email):
    """
    Handles a subscription request from an email link.
    If the email exists, it re-subscribes them.
    If the email does not exist, it creates a new subscriber.
    """
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber:
        subscriber.subscribed = True
        db.session.commit()
        return "<h1>You're Back!</h1><p>Thank you for re-subscribing.</p>"
    else:
        new_subscriber = Subscriber(email=email, subscribed=True)
        db.session.add(new_subscriber)
        db.session.commit()
        return "<h1>Success!</h1><p>Thank you for subscribing.</p>"

@app.route('/unsubscribe/<email>', methods=['GET'])
def unsubscribe(email):
    """Handles an unsubscription request from an email link."""
    subscriber = Subscriber.query.filter_by(email=email).first()
    if subscriber:
        subscriber.subscribed = False
        db.session.commit()
        return "<h1>Unsubscribed</h1><p>You have been successfully unsubscribed.</p>"
    else:
        # If they aren't in the DB, they are already effectively unsubscribed.
        return "<h1>Already Unsubscribed</h1><p>Your email was not found in our subscriber list.</p>"

# --- 4. Command Line Interface (CLI) for DB setup ---
@app.cli.command('init-db')
def init_db_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")

# --- 5. Main Execution Block (IMPORTANT!) ---
# This block runs the web server when you execute `python app.py`
if __name__ == '__main__':
    # We add a check here to remind the user to create the DB first.
    db_path = os.path.join(basedir, 'subscribers.db')
    if not os.path.exists(db_path):
        print("=" * 50)
        print("DATABASE FILE NOT FOUND!")
        print(f"Expected at: {db_path}")
        print("Please run 'flask --app app init-db' in your terminal first.")
        print("=" * 50)
    
    app.run(debug=True)