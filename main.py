from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://topmoviesdatabase_user:rRX7k4Xh8OaPRrkoCS1HzBgQkWlXO1rO@dpg-cq38un4s1f4s73fba8cg-a/topmoviesdatabase","sqlite:///movies.db")

db = SQLAlchemy(model_class=Base)
db.init_app(app)

img_url = "https://image.tmdb.org/t/p/w500"


class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )

# with app.app_context():
#     db.session.add(new_movie)
#     db.session.add(second_movie)
#     db.session.commit()


# CREATE TABLE
class EditRating(FlaskForm):
    new_rating = StringField(u'Your Rating out of 10 e.g. 7.3', validators=[DataRequired()])
    new_review = StringField(u'Your Review', validators=[DataRequired()])
    submit = SubmitField('Update', validators=[DataRequired()])


class AddMovie(FlaskForm):
    movieTitle = StringField(u"Movie Title", validators=[DataRequired()])
    add_movie = SubmitField(u"Add")


@app.route("/")
def home():
    list = []
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    all_movies = result.scalars().all()
    for i in db.session.execute(db.select(Movie.rating)).scalars():
        list.append(i)
    list.sort()

    rank = len(list)
    for i in list:
        db.session.execute(db.select(Movie).where(Movie.rating == i)).scalar().ranking = rank
        db.session.commit()
        rank -= 1

    all_movies = db.session.execute(db.select(Movie).order_by(Movie.ranking)).scalars()

    return render_template("index.html", movies=all_movies)


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    form = EditRating()
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movie, movie_id)
    if request.method == 'POST':
        movie.rating = float(form.new_rating.data)
        movie.review = form.new_review.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template("edit.html", form=form, movie=movie)


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()

    return redirect(url_for("home"))


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = AddMovie()
    if request.method == 'POST':
        movie_title = form.movieTitle.data

        URL = "https://api.themoviedb.org/3/search/movie?"

        header = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxMzEzYzJjZDdlMGU4MWVlMDI0ZDMwOGNiZjY3ZGE5OCIsIm5iZiI6MTcyMDAxMzA0Ni45NjA1MSwic3ViIjoiNjY4NTQ5ZmY3NTYxZjAyNGE4YmIwMjU4Iiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.Dwevp4iWb7itXh52wNdLXB3kmdwOGLs-UHoCat92I2U"
        }

        response = requests.get(URL, params={"query": movie_title}, headers=header)
        data = response.json()["results"]
        print(data)
        return render_template('select.html', form=form, options=data)

    return render_template("add.html", form=form)


@app.route('/find', methods=['GET', 'POST'])
def find():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        header = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIxMzEzYzJjZDdlMGU4MWVlMDI0ZDMwOGNiZjY3ZGE5OCIsIm5iZiI6MTcyMDAxMzA0Ni45NjA1MSwic3ViIjoiNjY4NTQ5ZmY3NTYxZjAyNGE4YmIwMjU4Iiwic2NvcGVzIjpbImFwaV9yZWFkIl0sInZlcnNpb24iOjF9.Dwevp4iWb7itXh52wNdLXB3kmdwOGLs-UHoCat92I2U"
        }

        response = requests.get(movie_api, headers=header)
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            year=data["release_date"].split("-")[0],
            img_url=f"{img_url}{data['poster_path']}",
            description=data["overview"],
            rating=7.2,
            review="good",
            ranking=1

        )
        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for("edit", id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
