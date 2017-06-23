"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} email={}>".format(self.user_id, self.email)

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True, unique=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def similarity(self, other_user):
        """Return Pearson rating for user compared to other user."""

        user_ratings = {}
        paired_ratings = []

        for rating in self.ratings:
            user_ratings[rating.movie_id] = rating

        for rating in other_user.ratings:
            user_rating = user_ratings.get(rating.movie_id)
            if user_rating:
                paired_ratings.append((user_rating.score, rating.score))

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    # def predict_rating(self, movie_id):
    #     """Sorte the similarity of group of users."""

    #     similarity_desc = []

    #     movie = Movie.query.filter_by(movie_id=movie_id).one()

    #     other_users = [rating.user for rating in movie.ratings]

    #     user = User.query.filter_by(user_id=self.user_id).one()

    #     if user in other_users:
    #         other_users.remove(user)

    #     for other_user in other_users:
    #         similarity_desc.append((self.similarity(other_user), other_user.user_id))

    #     similarity_desc.sort(reverse=True)

    #     most_similar_user = similarity_desc[0]

    #     similarity, similar_userid = most_similar_user

    #     movie_rating = Rating.query.filter_by(user_id=similar_userid, movie_id=movie_id).one()

    #     print similarity, similar_userid

    #     return similarity * movie_rating.score

    def predict_rating(self, movie_id):
        """Sorte the similarity of group of users."""

        similarity_desc = []

        movie = Movie.query.filter_by(movie_id=movie_id).one()

        other_users = [rating.user for rating in movie.ratings]

        user = User.query.filter_by(user_id=self.user_id).one()

        if user in other_users:
            other_users.remove(user)

        for other_user in other_users:
            for movie_rating in other_user.ratings:
                similarity_desc.append((self.similarity(other_user), movie_rating.score))

        pos = sum([sim * score for sim, score in similarity_desc if sim > 0])

        neg = sum([-sim * abs(score - 6) for sim, score in similarity_desc if sim < 0])

        denominator = sum([abs(sim) for sim, score in similarity_desc])

        return (pos + neg)/denominator


# Put your Movie and Rating model classes here.
class Movie(db.Model):
    """Movies of ratings website."""

    __tablename__ = "movies"

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id={} title={}>".format(self.movie_id, self.title)

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.String(256), nullable=True)


class Rating(db.Model):
    """Movies of ratings website."""

    __tablename__ = "ratings"

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating rating_id={} score={}>".format(self.rating_id, self.score)

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))
    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

 # def sorte_similarity(movie_id, user_id):
 #    """Sorte the similarity of group of users."""

 #    similarity_desc = []

 #    movie = Movie.query.filter_by(movie_id=movie_id).one()

 #    user = User.query.get(user_id)

 #    other_users = [rating.user for rating in movie.ratings]

 #    for other_user in other_users:
 #        similarity_desc.append((user.similarity(other_user), other_user.user_id))

 #    similarity_desc.sort(reverse=True)


 #    return similarity_desc




if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
