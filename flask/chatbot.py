# Local Imports
# import calendarprogram

# Standard Library Imports
import os
import sqlite3
from os import urandom
from dotenv import load_dotenv
import os.path

# Third-Party Imports
from flask import Flask, jsonify, render_template, redirect, request, session, url_for, g
from datetime import datetime
app = Flask(__name__)
app.secret_key = urandom(24)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
DATABASE = 'profiles.db'
app.config['DATABASE'] = DATABASE

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.executescript(f.read().decode('utf-8'))
    
@app.route("/")
def mainpage():
    return render_template("chatbot.html")

@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    if request.method == "POST":
        if not request.form.get("message"):
            return render_template("error.html")

        userInput = request.form.get("message")
        print("User Input:", userInput)
        return render_template("chatbot.html")
    else:
        return

init_db()

if __name__ == "__main__":
    app.run(debug=True)
