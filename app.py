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
    return "Welcome to the Vulnerable Lab! Visit /login to view the new login page."


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    error_message = ""

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            error_message = "Please enter both username and password."
        elif username == 'admin' and password == 'password123':
            return "<h2>Login successful. Welcome, admin!</h2>"
        else:
            error_message = "Invalid username or password."

    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>Login</title>
          <style>
            :root {
              color-scheme: light;
            }
            * {
              box-sizing: border-box;
            }
            body {
              margin: 0;
              min-height: 100vh;
              display: grid;
              place-items: center;
              font-family: Arial, sans-serif;
              background: linear-gradient(145deg, #f0f4ff, #dce7ff);
            }
            .login-card {
              width: min(92vw, 360px);
              background: #ffffff;
              border-radius: 14px;
              padding: 24px;
              box-shadow: 0 16px 40px rgba(21, 43, 99, 0.15);
            }
            h1 {
              margin: 0 0 18px;
              font-size: 1.4rem;
              color: #1f2a44;
              text-align: center;
            }
            label {
              display: block;
              margin-bottom: 6px;
              font-size: 0.9rem;
              color: #2f3b52;
            }
            input {
              width: 100%;
              border: 1px solid #cbd6f1;
              border-radius: 8px;
              padding: 10px 12px;
              margin-bottom: 14px;
              font-size: 0.95rem;
            }
            input:focus {
              outline: none;
              border-color: #5d7cff;
              box-shadow: 0 0 0 3px rgba(93, 124, 255, 0.2);
            }
            button {
              width: 100%;
              border: none;
              border-radius: 8px;
              background: #4f6bff;
              color: white;
              font-size: 0.95rem;
              font-weight: 600;
              padding: 11px;
              cursor: pointer;
            }
            button:hover {
              background: #3f5cf0;
            }
            .error {
              margin-bottom: 12px;
              background: #ffe7e7;
              color: #9f1b1b;
              border: 1px solid #ffc5c5;
              border-radius: 8px;
              padding: 8px 10px;
              font-size: 0.86rem;
            }
            .hint {
              margin-top: 12px;
              text-align: center;
              font-size: 0.8rem;
              color: #58627a;
            }
          </style>
        </head>
        <body>
          <form class="login-card" method="post">
            <h1>Account Login</h1>
            {% if error_message %}
            <div class="error">{{ error_message }}</div>
            {% endif %}

            <label for="username">Username</label>
            <input id="username" name="username" type="text" placeholder="Enter your username" required />

            <label for="password">Password</label>
            <input id="password" name="password" type="password" placeholder="Enter your password" required />

            <button type="submit">Sign In</button>
            <div class="hint">Demo credentials: admin / password123</div>
          </form>
        </body>
        </html>
        """,
        error_message=error_message,
    )


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
