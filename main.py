
from wtforms import DecimalField, RadioField, SelectField, TextAreaField, FileField
from wtforms.validators import InputRequired
from werkzeug.security import generate_password_hash
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from flask_bootstrap import Bootstrap4

from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
# Import your forms from the forms.py



app = Flask(__name__)
app.config['SECRET_KEY'] = 'daedaedae'

bootstrap = Bootstrap4(app)

ckeditor = CKEditor(app)


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)




class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///massarmy.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


def init(self, id):
    self.id = id
    self.active = True  # Example attribute to mark user as active


# CONFIGURE TABLES
class User(UserMixin,db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    username: Mapped[str] = mapped_column(String(100))
    x: Mapped[str] = mapped_column(String(100))
    telegram: Mapped[str] = mapped_column(String(100))

@property
def is_active(self):
        return self.active



class Task(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    Instructions: Mapped[str] = mapped_column(String(500), nullable=False)

with app.app_context():
    db.create_all()


class MyForm(FlaskForm):
    Task_Name = StringField('Task Name', validators=[InputRequired()])
    Instructions = StringField('instructions', validators=[InputRequired()])
    button = SubmitField('Submit Task')


class Login(FlaskForm):
    Email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    button = SubmitField('Login')


class Join(FlaskForm):
    Email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    telegram = StringField('Telegram Username', validators=[InputRequired()])
    x = StringField('X username', validators=[InputRequired()])
    username = StringField('username', validators=[InputRequired()])
    button = SubmitField('Register')
@app.route("/",methods=['GET', 'POST'])
def begin():
    return render_template("index.html")

@app.route("/register",methods=['GET', 'POST'])
def register():
  form = Join()
  if form.validate_on_submit():
      result = db.session.execute(db.select(User).where(User.email == form.Email.data))
      user = result.scalar()
      if user:
          # User already exists
          flash("You've already signed up with that email, log in instead!")
          return redirect(url_for('login'))

      hash_and_salted_password = generate_password_hash(
          form.password.data,
          method='pbkdf2:sha256',
          salt_length=8
      )
      new_user = User(
          email=form.Email.data,
          password=hash_and_salted_password,
          x = form.x.data,
          telegram = form.telegram.data,
          username=form.username.data,

      )
      db.session.add(new_user)
      db.session.commit()
      login_user(new_user)

      return redirect(url_for("home"))
  return render_template('register.html',form = form)
@app.route("/Login",methods=['GET', 'POST'])
def login():
  form = Login()
  if form.validate_on_submit():
      password = form.password.data
      result = db.session.execute(db.select(User).where(User.email == form.Email.data))

      user = result.scalar()
      if not user:
          flash("That email does not exist, please try again.")
          return redirect(url_for('login'))

      elif not check_password_hash(user.password, password):
          flash('Password incorrect, please try again.')
          return redirect(url_for('login'))
      else:
          login_user(user)
          return redirect(url_for('home'))
  return render_template('Login.html',form = form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('begin'))

@app.route("/home",methods=['GET', 'POST'])
@login_required
def home():
  return render_template('home.html',username= current_user.username)
@app.route("/add",methods=['GET', 'POST'])
@login_required
def add():
    form = MyForm()
    if form.validate_on_submit():
        new_task =  Task(
            Name = form.Task_Name.data,
            Instructions = form.Instructions.data,

        )
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for("tasks"))

    return render_template('add.html', form=form,current_user=current_user.username)
@app.route('/tasks')
@login_required
def tasks():
    result = db.session.execute(db.select(Task))
    tasks = result.scalars().all()
    return render_template('tasks.html',task=tasks)
@app.route("/post/<int:tk_id>", methods=["GET", "POST"])
def show_task(tk_id):
    requested_task = db.get_or_404(Task, tk_id)

    return render_template("task-list.html", tk=requested_task, current_user=current_user)



if __name__ == "__main__":
    app.run(debug=True)