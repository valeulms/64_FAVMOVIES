from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

# themoviedatabase user valeulms password pollo4ever email solita

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-collection.db"
db = SQLAlchemy()
db.init_app(app)
Bootstrap5(app)

# TODO: MOVIE DATABASE
API_KEY = "414d4dd7c9f4a006d3a252bc333771f5"
TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0MTRkNGRkN2M5ZjRhMDA2ZDNhMjUyYmMzMzM3NzFmNSIsInN1YiI6IjY1NWZhYjdkNzA2ZTU2MDBmZTAxYzBmNSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.afDI-FfIJOdiqeknVIji9OlObZEGZ98RLz9bFimnInI"
# print(response.raise_for_status())


class MovieForm(FlaskForm):
    rating = StringField(label='Rating')
    review = StringField(label='Review')
    button = SubmitField(label='Submit')


class AddMovie(FlaskForm):
    name = StringField(label='Movie Name')
    button = SubmitField('Add Movie')


class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=False)

# with app.app_context():
#    db.create_all()                  #create database then comment lines


@app.route("/")
def home():
    # TODO: ADD MOVIE HERE IF YOU WANT
    result = db.session.execute(db.select(Movie).order_by(Movie.rating))
    movies = result.scalars().all()
    i = 10
    for movie in movies:
        movie.ranking = i
        i -= 1
    return render_template("index.html", list_of_movies=movies)


@app.route("/edit?<num>", methods=["GET", "POST"])
def edit(num):
    movie_to_edit = db.session.execute(db.select(Movie).where(Movie.id == num)).scalar()
    movie_form = MovieForm()
    if movie_form.validate_on_submit():
        movie_to_edit.rating = float(movie_form.rating.data)
        movie_to_edit.review = movie_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie_to_edit, form=movie_form)


@app.route('/delete?<num>')
def delete(num):
    movie_to_delete = db.session.execute(db.select(Movie).where(Movie.id == num)).scalar()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=["GET", "POST"])
def add():
    add_form = AddMovie()
    if add_form.validate_on_submit():
        name = add_form.name.data
        response = requests.get(url=f"https://api.themoviedb.org/3/search/movie?query={name}&api_key={API_KEY}")
        data = response.json()["results"]
        list = []
        for result in data:
            list.append({"id": str(result['id']),
                         "title": result['title'],
                         "year": result['release_date'].split("-")[0]})
        return render_template("select.html", list=list)
    return render_template("add.html", form=add_form)


@app.route('/movie/<identif>', methods=["GET", "POST"])
def chosen_movie(identif):
    response = requests.get(url=f"https://api.themoviedb.org/3/movie/{identif}", params={"api_key": API_KEY, "language": "en-US"})
    data = response.json()
    movie_to_add = Movie(title=data['original_title'],
                         year=data['release_date'].split("-")[0],
                         description=data['overview'],
                         img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}")
    db.session.add(movie_to_add)
    db.session.commit()
    return redirect(url_for('edit', num=movie_to_add.id))


if __name__ == '__main__':
    app.run(debug=True)
