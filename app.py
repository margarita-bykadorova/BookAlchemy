from flask import Flask, render_template, request, redirect, url_for
import os
from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)

@app.route("/")
def home():
    search_query = request.args.get("search")
    sort_option = request.args.get("sort")
    message = request.args.get("message")

    query = Book.query

    # Search filter
    if search_query:
        query = query.filter(Book.title.ilike(f"%{search_query}%"))

    # Sorting
    if sort_option == "title":
        query = query.order_by(Book.title)
    elif sort_option == "author":
        query = query.join(Author).order_by(Author.name)

    books = query.all()

    # No results message
    if search_query and not books:
        message = f"No books found matching '{search_query}'."

    return render_template("home.html", books=books, message=message)

@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":
        name = request.form["name"]
        birth_date = request.form["birthdate"]
        date_of_death = request.form.get("date_of_death")  # may be empty

        new_author = Author(
            name=name,
            birth_date=birth_date,
            date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()
        message = "Author added successfully!"
        return render_template("add_author.html", message=message)

    return render_template("add_author.html")

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form["title"]
        isbn = request.form["isbn"]
        publication_year = request.form["publication_year"]
        author_id = request.form["author_id"]

        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(new_book)
        db.session.commit()

        message = "Book added successfully!"
        authors = Author.query.all()
        return render_template("add_book.html", authors=authors, message=message)

    authors = Author.query.all()
    return render_template("add_book.html", authors=authors)

@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author   # save for later check

    db.session.delete(book)
    db.session.commit()

    # If the author has no more books, delete the author too
    if len(author.books) == 0:
        db.session.delete(author)
        db.session.commit()

    message = "Book deleted successfully!"
    return redirect(url_for("home", message=message))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
