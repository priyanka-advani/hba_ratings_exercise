"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask_debugtoolbar import DebugToolbarExtension
from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify, url_for)
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

    if User.query.filter_by(email=email).count() == 0:

        new_user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(new_user)
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

    user_info = User.query.filter_by(email=email).first()

    if user_info.password == password:

        session["user_id"] = user_info.user_id

        flash('You have successfully logged in')

        return redirect(url_for(".show_userinfo", user_id=user_info.user_id))

    else:
        flash('Your information is incorrect')

        return redirect("/login")


@app.route("/logout")
def logout_process():
    """User log out."""

    session.pop('user_id', None)
    flash('You have successfully logged out')
    return redirect("/")


@app.route("/users/<user_id>")
def show_userinfo(user_id):
    """Show each user info."""

    user = User.query.get(user_id)

    return render_template("user_info.html", user=user)


@app.route("/movies")
def movies():
    """Show list of movies."""

    movies = Movie.query.order_by("title").all()
    return render_template("movie_list.html", movies=movies)


@app.route("/movies/<movie_id>")
def show_movieinfo(movie_id):
    """Show each user info."""

    movie = Movie.query.get(movie_id)
    released_date = movie.released_at.strftime("%A, %B %d, %Y")

    return render_template("movie_info.html", movie=movie, released_date=released_date)


@app.route("/rate", methods=["POST"])
def rate():
    """add or update movie rating."""

    score = int(request.form.get("score"))
    user_id = int(session.get("user_id"))
    movie_id = int(request.form.get("movie_id"))
    movie_rate = Rating.query.filter_by(movie_id=movie_id, user_id=user_id)

    if movie_rate.count() == 0:

        new_rating = Rating(movie_id=movie_id, user_id=user_id, score=score)
        db.session.add(new_rating)
        flash('You have successfully rated this movie.')
    else:
        movie_rate.one().score = score
        flash('You have updated your rating for this movie.')

    db.session.commit()

    return redirect("/movies")



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
