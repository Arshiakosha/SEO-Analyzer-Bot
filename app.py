from flask import Flask, render_template, redirect, url_for, session, request, flash
from flask_dance.contrib.google import make_google_blueprint, google
import os

app = Flask(__name__)
app.secret_key = "supersecret"  # Use a strong, random key in production

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Dev only

google_bp = make_google_blueprint(
    client_id="",
    client_secret="",
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email"
    ],
    redirect_url="/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

# Simple in-memory user store
users = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Username and password are required.', 'danger')
        elif username in users:
            flash('Username already exists.', 'danger')
        else:
            users[username] = password
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/login/google/authorized')
def google_authorized():
    if not google.authorized:
        return redirect(url_for('google.login', next=request.args.get('next') or url_for('dashboard')))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info from Google.", 400
    session['google_user'] = resp.json()
    next_url = request.args.get('next') or url_for('dashboard')
    return redirect(next_url)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session and 'google_user' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))
    # Redirect to Streamlit dashboard (localhost only!)
    return redirect("http://localhost:8501")

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)
