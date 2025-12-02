from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)   # 1. Create the app

# 2. Build absolute path to database
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, "data", "library.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + database_path

# 3. Initialize database
db = SQLAlchemy(app)

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.String(10))
    date_of_death = db.Column(db.String(10))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

@app.route("/")
def home():
    books = Book.query.all()
    return render_template("home.html", books=books)

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form["name"]
        birthdate = request.form["birthdate"]
        date_of_death = request.form.get("date_of_death")  # may be empty

        new_author = Author(
            name=name,
            birthdate=birthdate,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add_author.html")

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        author_id = request.form["author_id"]

        new_book = Book(title=title, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for("home"))

    # For GET: send the list of authors to the template
    authors = Author.query.all()
    return render_template("add_book.html", authors=authors)


with app.app_context():
    db.create_all()
