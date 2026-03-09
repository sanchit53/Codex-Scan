import sqlite3
import os
import subprocess
import pickle
import base64
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)
app.secret_key = "super_secret_unsecure_key_123"

db = sqlite3.connect(":memory:", check_same_thread=False)
db.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT)")
db.execute("INSERT INTO users VALUES (1, 'admin', 'password123')")


@app.route('/')
def index():
    return "Welcome to the Vulnerable Lab!"


@app.route('/user_lookup')
def user_lookup():
    user_id = request.args.get('id')
    query = f"SELECT username FROM users WHERE id = {user_id}"
    cursor = db.execute(query)
    return str(cursor.fetchone())


@app.route('/ping')
def network_test():
    hostname = request.args.get('host')
    command = f"ping -c 1 {hostname}"
    output = subprocess.check_output(command, shell=True)
    return output


@app.route('/hello')
def hello_user():
    name = request.args.get('name', 'Guest')
    template = f"<h1>Hello, {name}!</h1>"
    return render_template_string(template)


@app.route('/read_file')
def read_file():
    filename = request.args.get('file')
    with open(os.path.join('uploads', filename), 'r') as f:
        return f.read()


@app.route('/load_profile')
def load_profile():
    data = request.args.get('data')
    decoded_data = base64.b64decode(data)
    profile = pickle.loads(decoded_data)
    return "Profile loaded!"


@app.route('/debug_login')
def debug_login():
    user = "root"
    pw = "Admin@123"
    print(f"Attempting login for {user} with {pw}")
    return "Logging attempt..."


if __name__ == '__main__':
    app.run(debug=True, port=5000)
