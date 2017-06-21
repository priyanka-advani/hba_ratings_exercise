"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)
from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route("/users")
def users():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():
    """Show registration form."""

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """Submit registration form."""

    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    sql = """INSERT INTO users (email, password, age, zipcode)
             VALUES (:email, :password, :age, :zipcode)"""

    if User.query.filter_by(email=email).count() == 0:

        db.session.execute(sql, {'email': email,
                                 'password': password,
                                 'age': age,
                                 'zipcode': zipcode})
        db.session.commit()

        flash('You have successfully registered')

        return redirect("/")
    
    else:
        flash('Your email was already registered!')

        return redirect("/register")
    

@app.route("/login", methods=["GET"])
def login():
    """Show login form."""

    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_process():
    """User log in."""

    email = request.form.get("email")
    password = request.form.get("password")

    sql = "SELECT email, password FROM users WHERE email=:email"

    user_info = User.query.filter_by(email=email).first()

    if user_info.password == password:

    # add flask session
        session["user_id"] = user_info.user_id

        flash('You have successfully logged in')

        return redirect("/")
    
    else:
        flash('Your information is incorrect')

        return redirect("/login")


@app.route("/logout")
def logout_process():
    """User log out."""

    session.pop('user_id', None)
    flash('You have successfully logged out')
    return redirect("/")

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
