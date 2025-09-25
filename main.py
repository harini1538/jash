from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from flask_socketio import SocketIO, join_room, leave_room, send
import uuid

# Initialize the app and configure database
app = Flask(__name__)
app.config['SECRET_KEY'] = "my-secrets"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///video-meeting.db"
db = SQLAlchemy(app)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app)

# Login Manager for handling login/logout
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# User loader for flask-login
@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))

# User Model
class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

# Meeting Model
class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(50), unique=True, nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('register.id'), nullable=False)
    host = db.relationship('Register', backref='meetings', lazy=True)

with app.app_context():
    db.create_all()

# Registration Form
class RegistrationForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    first_name = StringField(label="First Name", validators=[DataRequired()])
    last_name = StringField(label="Last Name", validators=[DataRequired()])
    username = StringField(label="Username", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField(label="Password", validators=[DataRequired(), Length(min=8, max=20)])

# Login Form
class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])

# Home Route
@app.route("/")
def home():
    return redirect(url_for("login"))

# Login Route
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = Register.query.filter_by(email=email, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "error")

    return render_template("login.html", form=form)

# Logout Route
@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("You have been logged out successfully!", "info")
    return redirect(url_for("login"))

# Registration Route
@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        new_user = Register(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            password=form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created Successfully! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

# Dashboard Route
@app.route("/dashboard")
@login_required
def dashboard():
    meetings = Meeting.query.filter_by(host_id=current_user.id).all()
    return render_template("dashboard.html", meetings=meetings, first_name=current_user.first_name)

# Create Meeting Route
@app.route("/create_meeting", methods=["POST"])
@login_required
def create_meeting():
    room_id = str(uuid.uuid4())  # Generate a unique meeting ID
    new_meeting = Meeting(room_id=room_id, host_id=current_user.id)
    db.session.add(new_meeting)
    db.session.commit()
    flash(f"Meeting created with ID: {room_id}", "success")
    return redirect(url_for("dashboard"))

# Meeting Room Route
@app.route("/meeting/<room_id>")
@login_required
def meeting(room_id):
    meeting = Meeting.query.filter_by(room_id=room_id).first()
    if meeting:
        return render_template("meeting.html", room_id=room_id, username=current_user.username)
    else:
        flash("Invalid meeting ID", "error")
        return redirect(url_for("dashboard"))

# Join Meeting Route
@app.route("/join", methods=["GET", "POST"])
@login_required
def join():
    if request.method == "POST":
        room_id = request.form.get("roomID")
        meeting = Meeting.query.filter_by(room_id=room_id).first()
        if meeting:
            return redirect(url_for("meeting", room_id=room_id))
        else:
            flash("Meeting ID not found", "error")

    return render_template("join.html")

# WebSocket Events for Real-Time Chat
@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    send(f"{data['username']} has joined the room.", to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    send(f"{data['username']}: {data['message']}", to=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    send(f"{data['username']} has left the room.", to=room)

# Run the app with SocketIO support
if __name__ == "__main__":
    # Change the port if needed
    socketio.run(app, debug=True, port=5001)  # Change 5001 to another port if necessary
