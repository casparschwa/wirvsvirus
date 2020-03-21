import csv
import os
from docxtpl import DocxTemplate
from datetime import date

from flask import Flask, render_template, url_for, redirect, request, send_file
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_fontawesome import FontAwesome

from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import DataRequired, InputRequired, Email, Length


from werkzeug.security import generate_password_hash, check_password_hash

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'short-term-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'mydatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
fa = FontAwesome(app)


##### Define Forms #######
class LoginForm(FlaskForm):
    email = StringField("Email-Adresse", validators=[DataRequired()], id="id_email")
    password = PasswordField('Passwort', validators=[DataRequired()], id="id_password")
    remember_me = BooleanField('Angemeldet bleiben', id="id_remember")
    submit = SubmitField('Anmelden')

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)])
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])


#### Define Database Tables #######
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    Pages = db.relationship('Page', backref='creator', lazy=True)
    Rewards = db.relationship('Reward', backref='creator', lazy=True)



    def __repr__(self):
        return '<User {}>'.format(self.email) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Page(db.Model):
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    id = db.Column(db.Integer, primary_key=True)

class Reward(db.Model):
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    id = db.Column(db.Integer, primary_key=True)

##### Necessary WebApp Definitions ######
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Page': Page, 'Reward':Reward}

@login.user_loader
def load_user(id):
    return User.query.get(int(id))



######## Routes ##########
@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html", title="Home")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method="sha256")
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("index"))


    return render_template("signup.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            return render_template("login.html", title="Anmelden", form=form)

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))

    return render_template("login.html", title="Anmelden", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/createPage", methods=['GET', 'POST'])
@login_required
def createPage():
    return "<h1>In Process<h1>"

@app.route("/deletePage", methods=['GET', 'POST'])
@login_required
def deletePage():
    return "<h1>In Process<h1>"

@app.route("/<string:PageTitle>")
def pageTitle(PageTitle):
    return "<h1>In Process<h1>"

@app.route("/createReward/<int:RewardId>", methods=['GET', 'POST'])
def createReward(RewardId):
    return "<h1>In Process<h1>"

if __name__ == "__main__":
    app.run(debug=True)
